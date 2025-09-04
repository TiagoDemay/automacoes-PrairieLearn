import json
import os
import random

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
    if not os.path.exists(aprovados_path):
        print(f"Arquivo de aprovados não encontrado: {aprovados_path}. Pulando...")
        return

    exam_data = carregar_json(exam_path)
    aprovados = carregar_json(aprovados_path)
    allow_list = exam_data.get("allowAccess", [])

    novos_blocos = []

    for aluno in aprovados:
        email = aluno.get("email")
        if email and not aluno_ja_listado(email, allow_list):
            bloco = {
                "uids": [email],
                "startDate": "2025-01-16T08:00:00",
                "endDate": "2025-11-26T18:00:00",
                "password": gerar_senha_aleatoria(),
                "timeLimitMin": 10,
                "credit": 100
            }
            novos_blocos.append(bloco)

    if novos_blocos:
        print(f"{len(novos_blocos)} novos alunos adicionados a {os.path.basename(exam_path)}.")
        exam_data["allowAccess"].extend(novos_blocos)
    else:
        print(f"Nenhum novo aluno a adicionar em {os.path.basename(exam_path)}.")

    salvar_json(exam_data, output_path)
    print(f"Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    modulos = [1, 2, 3, 4]

    for modulo in modulos:
        exam_path = f"pl_gradebook/exam{modulo}.json"
        aprovados_path = f"pl_gradebook/aprovados_modulo{modulo}.json"
        output_path = f"pl_gradebook/exam{modulo}_atualizado.json"

        if os.path.exists(exam_path):
            atualizar_allow_access(exam_path, aprovados_path, output_path)
        else:
            print(f"Exam file {exam_path} não encontrado. Pulando...")
