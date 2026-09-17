import json
import os


def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def aluno_ja_listado(uid, allow_list):
    """
    Verifica se o aluno já está presente no allowAccess.
    """
    for bloco in allow_list:
        if uid in bloco.get("uids", []):
            return True

    return False


def atualizar_allow_access(
    exam_path,
    aprovados_path,
    output_path,
    exam_uuid
):
    """
    Adiciona ao allowAccess apenas os alunos aprovados
    que ainda não estão cadastrados.

    Cada aluno será associado ao exame correspondente
    no PrairieTest através do examUuid.
    """

    if not os.path.exists(aprovados_path):
        print(
            f"Arquivo de aprovados não encontrado: "
            f"{aprovados_path}. Pulando..."
        )
        return

    # Carrega o arquivo infoAssessment do Quiz
    exam_data = carregar_json(exam_path)

    # Carrega a lista de alunos aprovados no módulo
    aprovados = carregar_json(aprovados_path)

    # Garante que allowAccess exista
    allow_list = exam_data.setdefault("allowAccess", [])

    novos_blocos = []

    for aluno in aprovados:

        email = aluno.get("email")

        if not email:
            print("Aluno sem e-mail encontrado. Ignorando...")
            continue

        # Evita adicionar novamente quem já foi liberado
        if aluno_ja_listado(email, allow_list):
            print(f"{email} já possui acesso.")
            continue

        bloco = {
            "uids": [email],
            "examUuid": exam_uuid,
            "credit": 100
        }

        novos_blocos.append(bloco)

        print(f"Liberando acesso para: {email}")

    if novos_blocos:

        exam_data["allowAccess"].extend(novos_blocos)

        print(
            f"{len(novos_blocos)} novos alunos adicionados "
            f"a {os.path.basename(exam_path)}."
        )

    else:

        print(
            f"Nenhum novo aluno a adicionar em "
            f"{os.path.basename(exam_path)}."
        )

    salvar_json(exam_data, output_path)

    print(f"Arquivo salvo em: {output_path}")


if __name__ == "__main__":

    # UUID de cada exame criado no PrairieTest
    #
    # IMPORTANTE:
    # Cada Quiz deve possuir o seu próprio examUuid.
    #
    exams = {
        1: "c22bcdc7-087b-45e7-9096-caf862929987",
        2: "8feefef2-dac0-4a80-a2a5-9c95240e315d",
        3: "55c6bb7b-f2ff-49b6-a706-90e3a66821af",
        4: "6478b28a-1a74-4033-8a66-75d37ecb4718"
    }

    for modulo, exam_uuid in exams.items():

        exam_path = (
            f"pl_gradebook/exam{modulo}.json"
        )

        aprovados_path = (
            f"pl_gradebook/aprovados_modulo{modulo}.json"
        )

        output_path = (
            f"pl_gradebook/exam{modulo}_atualizado.json"
        )

        print()
        print("=" * 60)
        print(f"Processando QUIZ-{modulo}")
        print("=" * 60)

        if os.path.exists(exam_path):

            atualizar_allow_access(
                exam_path=exam_path,
                aprovados_path=aprovados_path,
                output_path=output_path,
                exam_uuid=exam_uuid
            )

        else:

            print(
                f"Arquivo {exam_path} não encontrado. "
                f"Pulando QUIZ-{modulo}..."
            )
