from __future__ import annotations
from pathlib import Path

def _plural(module_name: str) -> str:
    return f"{module_name}s"

def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]

def _html_input(field: dict) -> str:
    """필드 타입에 맞는 HTML input 생성 (Create용)"""
    name = field["name"]
    jtype = field["type"]

    if jtype == "Boolean":
        return f"""
        <label class="cb">
            <input type="checkbox" name="{name}" value="true" />
            {name}
        </label>
        """
    return f'<input type="text" name="{name}" placeholder="{name}" required />'


def generate_reservation_module(project_dir: Path, base_package: str, spec: dict) -> None:
    module_name = spec["moduleName"]
    entity_name = spec["entityName"]
    fields = spec["fields"]

    plural = _plural(module_name)        # todos, reservations
    route = f"/{plural}"                 # /todos
    list_attr = plural                   # model attribute name
    redirect_to = f"redirect:{route}"

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

    # ===== 1) Entity (getter + setter) =====
    field_decls = "\n".join([f"    private {f['type']} {f['name']};" for f in fields])

    ctor_params = ", ".join([f"{f['type']} {f['name']}" for f in fields])
    ctor_body = "\n".join([f"        this.{f['name']} = {f['name']};" for f in fields])

    getters = "\n".join([
        f"""    public {f['type']} get{_cap(f['name'])}() {{
        return {f['name']};
    }}""" for f in fields
    ])

    setters = "\n".join([
        f"""    public void set{_cap(f['name'])}({f['type']} {f['name']}) {{
        this.{f['name']} = {f['name']};
    }}""" for f in fields
    ])

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

{setters}
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

    # ===== 3) Service (findById + update) =====
    create_params = ", ".join([f"{f['type']} {f['name']}" for f in fields])
    new_entity_args = ", ".join([f["name"] for f in fields])

    update_body = "\n".join([f"        entity.set{_cap(f['name'])}({f['name']});" for f in fields])

    service_code = f"""package {base_package}.service;

import {base_package}.domain.{entity_name};
import {base_package}.repository.{entity_name}Repository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Transactional
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

    public void delete(Long id) {{
        repository.deleteById(id);
    }}

    public {entity_name} findById(Long id) {{
        return repository.findById(id).orElseThrow();
    }}

    public void update(Long id, {create_params}) {{
        {entity_name} entity = repository.findById(id).orElseThrow();
{update_body}
    }}
}}
"""
    (service_dir / f"{entity_name}Service.java").write_text(service_code, encoding="utf-8")

    # ===== 4) Controller (list/create/delete + edit/update) =====
    req_params = []
    call_args = []

    for f in fields:
        name = f["name"]
        jtype = f["type"]

        if jtype == "Boolean":
            req_params.append(f"@RequestParam(required=false) Boolean {name}")
            call_args.append(f"({name} != null && {name})")
        else:
            req_params.append(f"@RequestParam {jtype} {name}")
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
        return "{redirect_to}";
    }}

    @PostMapping("/{{id}}/delete")
    public String delete(@PathVariable Long id) {{
        service.delete(id);
        return "{redirect_to}";
    }}

    @GetMapping("/{{id}}/edit")
    public String edit(@PathVariable Long id, Model model) {{
        model.addAttribute("item", service.findById(id));
        return "{module_name}/edit";
    }}

    @PostMapping("/{{id}}/edit")
    public String update(@PathVariable Long id, {req_params_code}) {{
        service.update(id, {call_args_code});
        return "{redirect_to}";
    }}
}}
"""
    (web_dir / f"{entity_name}Controller.java").write_text(controller_code, encoding="utf-8")

    # ===== 5) View: list.html (CSS 적용) =====
    inputs_html = "\n       ".join([_html_input(f) for f in fields])

    item_parts = []
    for f in fields:
        fname = f["name"]
        item_parts.append(f'<span th:text="${{{{x.{fname}}}}}"></span>')
    list_line = " / ".join(item_parts)

    delete_action = f"@{{|{route}/${{x.id}}/delete|}}"
    edit_href = f"@{{|{route}/${{x.id}}/edit|}}"

    view_code = f"""<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>

<div th:replace="layout/base :: header"></div>

<div class="container">
  <div class="card">
    <h2>{entity_name}s</h2>

    <form class="row" method="post" action="{route}">
        {inputs_html}
        <button class="btn btn-success" type="submit">Add</button>
    </form>

    <ul class="list">
        <li th:each="x : ${{{list_attr}}}">
            <div>
              {list_line}
            </div>

            <div class="actions">
              <a class="btn small" th:href="{edit_href}">Edit</a>
              <form th:action="{delete_action}" method="post" style="display:inline;">
                <button class="btn btn-danger small" type="submit">Delete</button>
              </form>
            </div>
        </li>
    </ul>
  </div>
</div>

<div th:replace="layout/base :: footer"></div>

</body>
</html>
"""
    (view_dir / "list.html").write_text(view_code, encoding="utf-8")

    # ===== 6) View: edit.html (CSS 적용) =====
    edit_inputs = []
    for f in fields:
        name = f["name"]
        jtype = f["type"]
        if jtype == "Boolean":
            edit_inputs.append(f"""
            <label class="cb">
                <input type="checkbox" name="{name}" value="true" th:checked="${{item.{name}}}" />
                {name}
            </label>
            """)
        else:
            edit_inputs.append(f'<input type="text" name="{name}" placeholder="{name}" th:value="${{item.{name}}}" required />')

    edit_inputs_html = "\n       ".join(edit_inputs)
    edit_action = f"@{{|{route}/${{item.id}}/edit|}}"

    edit_view = f"""<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>

<div th:replace="layout/base :: header"></div>

<div class="container">
  <div class="card">
    <h2>Edit {entity_name}</h2>

    <form class="row" th:action="{edit_action}" method="post">
        {edit_inputs_html}
        <button class="btn btn-success" type="submit">Save</button>
        <a class="btn small" th:href="@{{{route}}}">Back</a>
    </form>
  </div>
</div>

<div th:replace="layout/base :: footer"></div>

</body>
</html>
"""
    (view_dir / "edit.html").write_text(edit_view, encoding="utf-8")

def _html_input(field: dict) -> str:
    """
    [Create 폼용 input 생성]
    - spec의 field 정보를 기반으로 HTML input 태그 생성
    """
    name = field["name"]
    jtype = field["type"]

    if jtype == "Boolean":
        return f"""
        <label class="cb">
            <input type="checkbox" name="{name}" value="true" />
            {name}
        </label>
        """
    
    return f'<input type="text" name="{name}" placeholder="{name}" required />'


def generate_home_page(project_dir: Path, base_package: str, modules: list[dict]):
    """
    [홈 페이지 생성]
    - modules 목록을 기반으로 / (index) 화면에 링크를 자동 생성
    """
    src_java = project_dir / "src" / "main" / "java"
    src_res = project_dir / "src" / "main" / "resources"
    base_path = Path(*base_package.split("."))

    web_dir = src_java / base_path / "web"
    view_dir = src_res / "templates"

    web_dir.mkdir(parents=True, exist_ok=True)
    view_dir.mkdir(parents=True, exist_ok=True)

    # 링크 데이터 생성: (Label, path)
    links = []
    for m in modules:
        module_name = m["moduleName"]
        plural = f"{module_name}s"
        path = f"/{plural}"
        label = plural[:1].upper() + plural[1:] #Reservations, Todos
        links.append((label, path))

    controller_code = f"""package {base_package}.web;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

/**
* [HomeController]
* - 홈(/)에서 생성된 모듈 링크 목록을 보여준다
*/
@Controller
public class HomeController {{
    /**
    * 홈 페이지
    */
    @GetMapping("/")
    public String home(Model model) {{
        model.addAttribute("links", List.of(
        {",\n".join([f'      new String[]{{"{label}", "{path}"}}' for (label, path) in links])}
        ));
        return "index";
    }}
}}
"""
    (web_dir / "HomeController.java").write_text(controller_code, encoding="utf-8")

    # ==== index.html ====
    index_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>

<div th:replace="layout/base :: header"></div>

<main>
    <h2>Generated Modules</h2>

    <ul>
        <li th:each="l : ${links}">
            <a th:href="${l[1]}" th:text="${l[0]}"></a>
        </li>
    </ul>
</main>

<div th:replace="layout/base :: footer"></div>

</body>
</html>
"""
    (view_dir / "index.html").write_text(index_html, encoding="utf-8")

"""[공통 CSS 생성] 모든 화면에서 사용하는 기본 스타일"""
def ensure_app_css(project_dir: Path) -> None:
    css_dir = project_dir / "src" / "main" / "resources" / "static"
    css_dir.mkdir(parents=True, exist_ok=True)

    css = """/* app.css - generated */
:root { --bg:#0b1220; --card:#121a2b; --text:#e6eaf2; --muted:#a7b0c3; --line:#25314d; --btn:#3b82f6; --btn2:#22c55e; --danger:#ef4444; }

* { box-sizing: border-box; }
body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background: var(--bg); color: var(--text); }
a { color: inherit; text-decoration: none; }
.container { max-width: 900px; margin: 0 auto; padding: 24px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
.header { display:flex; justify-content: space-between; align-items:center; margin-bottom: 16px; }
.brand { font-weight: 800; letter-spacing: 0.5px; }
.nav a { margin-left: 12px; color: var(--muted); }
h2 { margin: 0 0 14px; }
form.row { display:flex; gap:10px; align-items:center; flex-wrap: wrap; margin-bottom: 14px; }
input[type="text"] { padding:10px 12px; border-radius: 10px; border:1px solid var(--line); background:#0f1729; color:var(--text); }
label.cb { display:flex; align-items:center; gap:8px; color: var(--muted); }
button { padding:10px 12px; border:0; border-radius: 10px; cursor:pointer; font-weight:700; }
.btn { background: var(--btn); color:white; }
.btn-success { background: var(--btn2); color:white; }
.btn-danger { background: var(--danger); color:white; }
.list { list-style:none; padding:0; margin:0; }
.list li { display:flex; justify-content: space-between; align-items:center; padding: 10px 0; border-bottom: 1px solid var(--line); }
.meta { color: var(--muted); font-size: 14px; }
.actions { display:flex; gap:8px; }
.small { padding:8px 10px; font-size: 13px; border-radius: 10px; }
"""
    (css_dir / "app.css").write_text(css, encoding="utf-8")
