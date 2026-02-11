from __future__ import annotations
from pathlib import Path


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def generate_reservation_module(project_dir: Path, base_package: str, spec: dict) -> None:

    module_name = spec["moduleName"]
    entity_name = spec["entityName"]
    fields = spec["fields"]

    src_java = project_dir / "src" / "main" / "java"
    src_res = project_dir / "src" / "main" / "resources"

    base_path = Path(*base_package.split("."))
    domain_dir = src_java / base_path / "domain"
    repo_dir = src_java / base_path / "repository"
    service_dir = src_java / base_path / "service"
    web_dir = src_java / base_path / "web"
    view_dir = src_res / "templates" / module_name

    for d in [domain_dir, repo_dir, service_dir, web_dir, view_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ===== 1) Entity =====
    field_decls = "\n".join(
        [f"    private {f['type']} {f['name']};" for f in fields]
    )

    ctor_params = ", ".join(
        [f"{f['type']} {f['name']}" for f in fields]
    )

    ctor_body = "\n".join(
        [f"        this.{f['name']} = {f['name']};" for f in fields]
    )

    getters = "\n".join(
        [f"""    public {f['type']} get{_cap(f['name'])}() {{
        return {f['name']};
    }}""" for f in fields]
    )

    entity_code = f"""package {base_package}.domain;

import jakarta.persistence.*;

@Entity
public class {entity_name} {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

{field_decls}

    protected {entity_name}() {{}}

    public {entity_name}({ctor_params}) {{
{ctor_body}
    }}

    public Long getId() {{
        return id;
    }}

{getters}
}}
"""

    (domain_dir / f"{entity_name}.java").write_text(entity_code, encoding="utf-8")

    # ===== 2) Repository =====
    repo_code = f"""package {base_package}.repository;

import {base_package}.domain.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;

public interface {entity_name}Repository extends JpaRepository<{entity_name}, Long> {{
}}
"""

    (repo_dir / f"{entity_name}Repository.java").write_text(repo_code, encoding="utf-8")

    # ===== 3) Service =====
    create_params = ", ".join(
        [f"{f['type']} {f['name']}" for f in fields]
    )

    new_entity_args = ", ".join(
        [f["name"] for f in fields]
    )

    service_code = f"""package {base_package}.service;

import {base_package}.domain.{entity_name};
import {base_package}.repository.{entity_name}Repository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class {entity_name}Service {{

    private final {entity_name}Repository repository;

    public {entity_name}Service({entity_name}Repository repository) {{
        this.repository = repository;
    }}

    public List<{entity_name}> findAll() {{
        return repository.findAll();
    }}

    public {entity_name} create({create_params}) {{
        return repository.save(new {entity_name}({new_entity_args}));
    }}
}}
"""

    (service_dir / f"{entity_name}Service.java").write_text(service_code, encoding="utf-8")

    # ===== 4) Controller =====
    controller_code = f"""package {base_package}.web;

import {base_package}.service.{entity_name}Service;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/reservations")
public class {entity_name}Controller {{

    private final {entity_name}Service service;

    public {entity_name}Controller({entity_name}Service service) {{
        this.service = service;
    }}

    @GetMapping
    public String list(Model model) {{
        model.addAttribute("reservations", service.findAll());
        return "{module_name}/list";
    }}

    @PostMapping
    public String create(@RequestParam String name,
                         @RequestParam String date) {{
        service.create(name, date);
        return "redirect:/reservations";
    }}
}}
"""

    (web_dir / f"{entity_name}Controller.java").write_text(controller_code, encoding="utf-8")

    # ===== 5) View =====
    view_code = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>

<div th:replace="layout/base :: header"></div>

<main>
    <h2>Reservations</h2>

    <form method="post" action="/reservations">
        <input type="text" name="name" placeholder="Name" required />
        <input type="text" name="date" placeholder="Date" required />
        <button type="submit">Add</button>
    </form>

    <ul>
        <li th:each="r : ${reservations}">
            <span th:text="${r.name}"></span> /
            <span th:text="${r.date}"></span>
        </li>
    </ul>
</main>

<div th:replace="layout/base :: footer"></div>

</body>
</html>
"""

    (view_dir / "list.html").write_text(view_code, encoding="utf-8")
