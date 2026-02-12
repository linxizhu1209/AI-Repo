from __future__ import annotations
from pathlib import Path

def _plural(module_name: str) -> str:
    """단순한 복수형 생성"""
    return f"{module_name}s"

def _html_input(field: dict) -> str:
    """ 필드 타입에 맞는 html input 생성"""
    name = field["name"]
    jtype = field["type"]

    if jtype == "Boolean":
        return f"""
        <label>
            <input type="checkbox" name="{name}" value="true" />
            {name}
        </label>
        """
    
    return f'<input type="text" name="{name}" placeholder="{name}" required />'

def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def generate_reservation_module(project_dir: Path, base_package: str, spec: dict) -> None:

    print("DEBUG SPEC:", spec)

    module_name = spec["moduleName"]
    entity_name = spec["entityName"]
    fields = spec["fields"]

    plural = f"{module_name}s"  # reservations, todos etc..
    route = f"/{plural}" # /reservations etc ...
    list_attr = plural

    print(f"[GEN] module={module_name}, entity={entity_name}, fields={len(fields)}")

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
    plural = _plural(module_name)
    route = f"/{plural}"
    list_attr = plural

    req_params = []
    call_args = []

    for f in fields:
        name = f["name"]
        jtype = f["type"]

        if jtype == "Boolean":
            # 체크박스는 미체크면 값이 안넘어옴 -> required = false
            req_params.append(f"@RequestParam(required=false) Boolean {name}")
            # null 이면 false 처리
            call_args.append(f'({name} != null && {name})')
        else:
            req_params.append(f'@RequestParam {jtype} {name}')
            call_args.append(name)

    req_params_code = ",\n                          ".join(req_params)
    call_args_code = ", ".join(call_args)

    controller_code = f"""package {base_package}.web;

import {base_package}.service.{entity_name}Service;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("{route}")
public class {entity_name}Controller {{

    private final {entity_name}Service service;

    public {entity_name}Controller({entity_name}Service service) {{
        this.service = service;
    }}

    @GetMapping
    public String list(Model model) {{
        model.addAttribute("{list_attr}", service.findAll());
        return "{module_name}/list";
    }}

    @PostMapping
    public String create({req_params_code}) {{
        service.create({call_args_code});
        return "redirect:{route}";
    }}
}}
"""

    (web_dir / f"{entity_name}Controller.java").write_text(controller_code, encoding="utf-8")

    # ===== 5) View =====

    plural = _plural(module_name)
    route = f"/{plural}"
    list_attr = plural   

    inputs_html = "\n       ".join([_html_input(f) for f in fields])

    item_parts = []
    for f in fields:
        fname = f["name"]
        item_parts.append(f'<span th:text="${{{{x.{fname}}}}}"></span>')
    list_line = " / ".join(item_parts)

    view_code = f"""<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>

<div th:replace="layout/base :: header"></div>

<main>
    <h2>{entity_name}s</h2>

    <form method="post" action="{route}">
        {inputs_html}
        <button type="submit">Add</button>
    </form>

    <ul>
        <li th:each="x : ${{list_attr}}">
            {list_line}    
        </li>
    </ul>
</main>

<div th:replace="layout/base :: footer"></div>

</body>
</html>
"""
    (view_dir / "list.html").write_text(view_code, encoding="utf-8")


def _html_input(field: dict) -> str:
    """필드 타입에 맞는 HTML input 생성"""
    name = field["name"]
    jtype = field["type"]

    if jtype == "Boolean":
        return f"""
        <label>
            <input type="checkbox" name="{name}" value="true" />
            {name}
        </label>
        """
    return f'<input type="text" name="{name}" placeholder="{name}" required />'