import os

def delete_files_by_attribute(directory, attribute1, start_num, end_num):
    """
    특정 속성1과 속성2 범위에 해당하는 .txt 파일을 삭제하는 함수.

    Parameters:
        directory (str): 파일들이 위치한 디렉토리 경로.
        attribute1 (str): 삭제할 파일의 속성1 값 (예: 'ripe_yulgwa_1').
        start_num (int): 삭제할 파일의 시작 속성2 번호.
        end_num (int): 삭제할 파일의 끝 속성2 번호.
    """
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt") and file_name.startswith(attribute1):
            try:
                base_name = file_name.rsplit(".txt", 1)[0]
                _, attribute2 = base_name.rsplit("_", 1)
                attribute2_int = int(attribute2)  # 속성2를 숫자로 변환

                # 속성2가 지정된 범위 내에 있으면 파일 삭제
                if start_num <= attribute2_int <= end_num:
                    file_path = os.path.join(directory, file_name)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            except ValueError:
                print(f"Skipping invalid file name: {file_name}")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

# 사용자 입력 받기
directory_path = input("Enter the directory path: ").strip()
attribute1 = input("Enter the attribute1 (e.g., ripe_yulgwa_1 or ripe_yulgwa_2): ").strip()
start = int(input("Enter the start number for attribute2 (e.g., 0 for 000000): ").strip())
end = int(input("Enter the end number for attribute2: ").strip())

# 파일 삭제 실행
delete_files_by_attribute(directory_path, attribute1, start, end)
