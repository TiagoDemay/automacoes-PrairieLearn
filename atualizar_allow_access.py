import json
import os
import random
from datetime import datetime

def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def gerar_senha_aleatoria():
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
            bloco = {
                "uids": [email],
                "startDate": "2025-08-01T08:00:00",
                "endDate": "2025-12-01T18:00:00",
                "password": gerar_senha_aleatoria(),
                "timeLimitMin": 10,
                "credit": 100
            }
            novos_blocos.append(bloco)

    if novos_blocos:
        print(f"{len(novos_blocos)} alunos novos adicionados ao allowAccess em {os.path.basename(output_path)}.")
        exam_data["allowAccess"].extend(novos_blocos)
    else:
        print(f"Nenhum novo aluno a ser adicionado em {os.path.basename(output_path)}.")

    salvar_json(exam_data, output_path)
    print(f"Arquivo atualizado salvo em: {output_path}")

if __name__ == "__main__":
    for i in range(1, 5):
        atualizar_allow_access(
            exam_path=f"pl_gradebook/exam{i}.json",
            aprovados_path=f"pl_gradebook/aprovados_roteiro{i}.json",
            output_path=f"pl_gradebook/exam{i}_atualizado.json"
        )
