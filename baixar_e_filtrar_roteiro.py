#!/usr/bin/env python3

import os
import json
import argparse
import requests
import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


def parse_args():
    parser = argparse.ArgumentParser(description="Baixa o gradebook e filtra alunos aprovados em um ou mais roteiros")
    parser.add_argument("-t", "--token", help="Token da API (ou defina a variável de ambiente PL_TOKEN)")
    parser.add_argument("-i", "--course-instance-id", required=True, help="ID da instância do curso")
    parser.add_argument("-r", "--roteiros", nargs="+", required=True, help="Lista de nomes de roteiros (ex: Roteiro1 Roteiro2...)")
    parser.add_argument("-o", "--output-dir", default="pl_gradebook", help="Diretório de saída")
    parser.add_argument("-s", "--server", default="https://us.prairielearn.com/pl/api/v1", help="URL base da API")
    return parser.parse_args()


def get_token(args):
    token = args.token or os.getenv("PL_TOKEN")
    if not token:
        raise EnvironmentError("Token não fornecido. Use --token ou defina a variável de ambiente PL_TOKEN.")
    return token


def download_gradebook(server, course_id, token):
    url = f"{server}/course_instances/{course_id}/gradebook"
    headers = {"Private-Token": token}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Erro ao acessar API: {response.status_code} - {response.text}")
    return response.json()


def salvar_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def filtrar_aprovados_por_roteiro(dados, roteiro_nome):
    aprovados = []
    for aluno in dados:
        nome = aluno.get("user_name")
        email = aluno.get("user_uid")
        assessments = aluno.get("assessments", [])
        for prova in assessments:
            score = prova.get("score_perc")
            if prova.get("assessment_name") == roteiro_nome and isinstance(score, (int, float)) and score > 70:
                aprovados.append({
                #    "name": nome,
                    "email": email,
                    "roteiro": roteiro_nome,
                    "score_perc": score,
                #    "points": prova.get("points"),
                #    "max_points": prova.get("max_points")
                })
                break
    return aprovados


def main():
    args = parse_args()
    token = get_token(args)
    os.makedirs(args.output_dir, exist_ok=True)

    gradebook = download_gradebook(args.server, args.course_instance_id, token)
    gradebook_path = os.path.join(args.output_dir, "gradebook.json")
    salvar_json(gradebook, gradebook_path)
    print(f"Gradebook salvo como JSON em: {gradebook_path}")

    for roteiro in args.roteiros:
        aprovados = filtrar_aprovados_por_roteiro(gradebook, roteiro)
        filename = f"aprovados_{roteiro.lower().replace(' ', '_')}.json"
        output_path = os.path.join(args.output_dir, filename)
        salvar_json(aprovados, output_path)
        print(f"{len(aprovados)} alunos aprovados em {roteiro} salvos em: {output_path}")


if __name__ == "__main__":
    main()
