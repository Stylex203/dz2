import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt
import configparser

def get_commits_with_file(repo_path, target_file):
    os.chdir(repo_path)
    commits_with_file = []
    try:
        git_log_command = [
            "git",
            "log",
            "--name-only",
            "--pretty=format:%H %s",
        ]
        result = subprocess.run(git_log_command, capture_output=True, text=True)
        log_data = result.stdout.strip().split("\n")

        current_commit = None
        for line in log_data:
            if line.strip() == "":
                current_commit = None
                continue

            if current_commit is None:
                parts = line.split(" ", 1)
                current_commit = {"hash": parts[0], "message": parts[1] if len(parts) > 1 else ""}
            else:
                if line.strip() == target_file:
                    commits_with_file.append((current_commit["hash"], current_commit["message"]))
                    current_commit = None

    except Exception as e:
        print(f"Ошибка при выполнении команды git log: {e}")

    return commits_with_file

def build_dependency_graph(repo_path, commits, output_file):
    G = nx.DiGraph()
    for commit_hash, message in commits:
        G.add_node(commit_hash, label=message)
    for i in range(len(commits) - 1):
        G.add_edge(commits[i + 1][0], commits[i][0])

    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, "label")
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=8, font_weight="bold")
    nx.draw_networkx_labels(G, pos, labels=labels)

    plt.savefig(output_file)
    print(f"Граф зависимостей сохранён в файл: {output_file}")

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    try:
        repo_path = config["Settings"]["RepoPath"]
        target_file = config["Settings"]["TargetFile"]
        output_file = config["Settings"]["OutputFile"]

        if not os.path.exists(repo_path):
            print(f"Указанный путь к репозиторию не существует: {repo_path}")
            return

        print(f"Поиск коммитов с изменениями файла: {target_file}...")
        commits = get_commits_with_file(repo_path, target_file)

        if not commits:
            print(f"Нет коммитов с изменениями файла: {target_file}")
            return

        print("Создание графа зависимостей...")
        build_dependency_graph(repo_path, commits, output_file)

    except KeyError as e:
        print(f"Отсутствует ключ в конфигурационном файле: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
