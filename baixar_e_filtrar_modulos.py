#!/usr/bin/env python3

import os
import json
import argparse
import requests
import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

def parse_args():
    parser = argparse.ArgumentParser(description="Baixa o gradebook do PrairieLearn e filtra alunos aprovados por módulo.")
    parser.add_argument("-t", "--token", help="Token da API (ou defina a variável de ambiente PL_TOKEN)")
    parser.add_argument("-i", "--course-instance-id", required=True, help="ID da instância do curso")
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
        json.dump(data, f, indent=2, ensure_ascii=False)

def aluno_aprovado_modulo(aluno, modulo_num):
    criterios = {
        f"Roteiro{modulo_num}": 100,
        f"Teoria{modulo_num}": 70,
        f"Tutorial{modulo_num}": 50
    }

    for nome_assessment, nota_minima in criterios.items():
        passou = False
        for prova in aluno.get("assessments", []):
            if prova.get("assessment_name") == nome_assessment:
                score = prova.get("score_perc")
                if score is not None and score >= nota_minima:
                    passou = True
                    break
        if not passou:
            return False
    return True

def filtrar_aprovados_por_modulo(gradebook, modulo_num):
    aprovados = []
    for aluno in gradebook:
        if aluno_aprovado_modulo(aluno, modulo_num):
            aprovados.append({
                "email": aluno.get("user_uid"),
                "modulo": modulo_num
            })
    return aprovados

def main():
    args = parse_args()
    token = get_token(args)
    os.makedirs(args.output_dir, exist_ok=True)

    gradebook = download_gradebook(args.server, args.course_instance_id, token)
    gradebook_path = os.path.join(args.output_dir, "gradebook.json")
    salvar_json(gradebook, gradebook_path)
    print(f"Gradebook salvo em: {gradebook_path}")

    for modulo in range(1, 5):
        aprovados = filtrar_aprovados_por_modulo(gradebook, modulo)
        output_path = os.path.join(args.output_dir, f"aprovados_modulo{modulo}.json")
        salvar_json(aprovados, output_path)
        print(f"{len(aprovados)} alunos aprovados no módulo {modulo} salvos em: {output_path}")

if __name__ == "__main__":
    main()
