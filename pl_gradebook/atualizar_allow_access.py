# pl_gradebook/atualizar_allow_access.py

import json
import os
import random

def carregar_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def gerar_senha():
    return str(random.randint(1000000, 9999999))

def aluno_ja_listado(uid, allow_list):
    for bloco in allow_list:
        if uid in bloco.get("uids", []):
            return True
    return False

def atualizar_allow_access(exam_path, aprovados_path, output_path):
    exam_data = carregar_json(exam_path)
    aprovados = carregar_json(aprovados_path)
    allow_list = exam_data.get("allowAccess", [])
    novos_blocos = []

    for aluno in aprovados:
        email = aluno.get("email")
        if email and not aluno_ja_listado(email, allow_list):
            novos_blocos.append({
                "uids": [email],
                "startDate": "2025-01-16T08:00:00",
                "endDate": "2025-06-11T18:00:00",
                "password": gerar_senha(),
                "timeLimitMin": 10,
                "credit": 100
            })

    if novos_blocos:
        exam_data["allowAccess"].extend(novos_blocos)

    salvar_json(exam_data, output_path)

def main():
    for i in range(1, 5):
        atualizar_allow_access(
            f"pl_gradebook/exam{i}.json",
            f"pl_gradebook/aprovados_roteiro{i}.json",
            f"curso/courseInstances/CompNuvem-2025a/assessments/arguicao{i}/infoAssessment.json"
        )

if __name__ == "__main__":
    main()
