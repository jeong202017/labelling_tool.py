import os

def summarize_txt_files(directory, output_file):
    """
    각 폴더별로 .txt 파일의 내용 여부를 분석하고, 결과를 요약하여 출력하는 함수.

    Parameters:
        directory (str): 분석할 상위 디렉토리 경로.
        output_file (str): 요약 결과를 저장할 파일 경로.
    """
    folder_summary = []

    # 상위 디렉토리 내 모든 하위 폴더 탐색
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)

        # 폴더인지 확인
        if os.path.isdir(folder_path):
            total_files = 0
            empty_files = 0
            non_empty_files = 0

            # 해당 폴더 내의 파일 탐색
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".txt"):
                    total_files += 1
                    file_path = os.path.join(folder_path, file_name)

                    # 파일 내용 확인
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                non_empty_files += 1
                            else:
                                empty_files += 1
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

            # 결과 저장
            folder_summary.append({
                "folder_name": folder_name,
                "total_files": total_files,
                "empty_files": empty_files,
                "non_empty_files": non_empty_files
            })

    # 결과를 출력 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Folder Analysis Summary\n")
        f.write("=" * 30 + "\n\n")
        for summary in folder_summary:
            f.write(f"Folder: {summary['folder_name']}\n")
            f.write(f"  Total .txt files: {summary['total_files']}\n")
            f.write(f"  Empty .txt files: {summary['empty_files']}\n")
            f.write(f"  Non-empty .txt files: {summary['non_empty_files']}\n\n")

    print(f"Summary written to {output_file}")

# 사용자 입력
directory_path = input("Enter the parent directory path: ").strip()
output_summary_path = input("Enter the output file path for the summary (e.g., summary.txt): ").strip()

# 함수 실행
summarize_txt_files(directory_path, output_summary_path)
