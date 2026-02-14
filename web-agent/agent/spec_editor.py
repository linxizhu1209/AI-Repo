"""지시 (instruction) 를 해석한 후 spec을 수정하는 모듈"""
from __future__ import annotations
import re
from typing import Any

""" 단일 모듈이면 [module], 멀티 모듈이면 modules 리스트를 반환"""
def _get_modules_list(spec: dict) -> list[dict] | None:
    if "modules" in spec:
        return spec["modules"]
    if "module" in spec:
        return [spec["module"]]
    return None

""" spec 에서 index번째 모듈을 주어진 module로 교체 """
def _set_module(spec: dict, index: int, module: dict) -> None:
    if "modules" in spec:
        spec["modules"][index] = module
    else:
        spec["module"] = module

""" 지시문을 해석하여 spec을 수정한 뒤 반환하는 함수 
    - (모듈명) 에 (필드명) 필드 추가 / (타입)으로 추가
    - (모듈명) 에 (필드명) 필드 삭제
"""
def apply_instruction(spec: dict, instruction: str) -> dict:
    instruction = instruction.strip()
    modules = _get_modules_list(spec)
    if not modules:
        return spec
    
    # --- 필드 추가 지시 -------
    add_match = re.search(
        r"(\w+?)에\s+(\w+)\s+필드\s+(?:(\w+)\s+으로\s+)?추가",
        instruction,
    )
    if add_match:
        module_name, field_name, type_str = add_match.group(1), add_match.group(2), add_match.group(3)
        field_type = type_str if type_str else "String"
        for i, m in enumerate(modules):
            if m.get("moduleName") == module_name:
                fields = list(m.get("fields", []))
                if any(f.get("name") == field_name for f in fields):
                    return spec
                fields.append({"name": field_name, "type": field_type})
                new_module = {**m, "fields": fields}
                _set_module(spec, i, new_module)
                return spec
        return spec

    # --- 필드 삭제 지시 ----
    del_match = re.search(
        r"(\w+)\s+\s+(\w+)\s+필드\s+삭제",
        instruction
    )
    if del_match:
        module_name, field_name = del_match.group(1), del_match.group(2)
        for i, m in enumerate(modules):
            if m.get("moduleNmae") == module_name:
                fields = [f for f in m.get("fields", []) if f.get("name") != field_name] # field_name과 일치하는 것은 제외시키고 일치하지 않는 것들만 남겨둠
                if len(fields) == len(m.get("fields", [])):
                    return spec # 없는 필드라면 무시
                _set_module(spec, i, {**m, "fields": fields})
                return spec
            return spec

    ## ---- 모듈 추가 (단일 spec만, modules 형태로 바꿈) ----
    # ex: todo 모듈 추가,  필드는 title:String, done:Boolean
    add_module_match = re.search(
        r"(\w+)\s+모듈\s+추가\s*,\s*필드\s+([\w:,]+)",
        instruction,
    )
    if add_module_match:
        module_name = add_module_match.group(1)
        fields_str = add_module_match.group(2)
        if any(m.get("moduleName") == module_name for m in modules):
            return spec # 이미 있는 모듈이면 리턴
        fields = []
        for part in fields_str.split(","):
            part = part.strip()
            if ":" in part:
                name, typ = part.split(":", 1)
                name, typ = name.strip(), typ.strip()
            else:
                name, typ = part, "String"
            if name and typ in ("String", "Boolean", "Integer", "Long"):
                fields.append({"name": name, "type": typ})
            elif name:
                fields.append({"name": name, "type": "String"})
        if not fields:
            return spec
        entity_name = module_name[:1].upper() + module_name[1:] # 클래스 이름 첫글자 대문자로
        new_module = {"moduleName": module_name, "entityName": entity_name, "fields": fields}
        if "modules" in spec:
            spec["modules"] = list(spec["modules"]) + [new_module]
        else:
            spec["modules"] = [spec["module"], new_module]
        return spec

    return spec


