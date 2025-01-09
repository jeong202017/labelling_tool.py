import os

def modify_class_by_attribute(directory, attribute1, start_num, end_num, new_class):
    """
    특정 속성1과 속성2 범위에 해당하는 .txt 파일의 첫 번째 값(클래스 정보)을 변경하는 함수.

    Parameters:
        directory (str): 파일들이 위치한 디렉토리 경로.
        attribute1 (str): 수정할 파일의 속성1 값 (예: 'ripe_yulgwa_1').
        start_num (int): 수정할 파일의 시작 속성2 번호.
        end_num (int): 수정할 파일의 끝 속성2 번호.
        new_class (int): 새롭게 지정할 클래스 값.
    """
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt") and file_name.startswith(attribute1):
            try:
                base_name = file_name.rsplit(".txt", 1)[0]
                _, attribute2 = base_name.rsplit("_", 1)
                attribute2_int = int(attribute2)  # 속성2를 숫자로 변환

                # 속성2가 지정된 범위 내에 있으면 클래스 정보 변경
                if start_num <= attribute2_int <= end_num:
                    file_path = os.path.join(directory, file_name)
                    
                    # 파일 내용 읽기
                    with open(file_path, 'r') as file:
                        lines = file.readlines()

                    # 첫 번째 값(클래스 정보) 변경
                    modified_lines = []
                    for line in lines:
                        parts = line.strip().split()
                        if parts:  # 빈 라인이 아닌 경우
                            parts[0] = str(new_class)
                            modified_lines.append(' '.join(parts))

                    # 변경된 내용 다시 저장
                    with open(file_path, 'w') as file:
                        file.writelines('\n'.join(modified_lines) + '\n')

                    print(f"Modified class in file: {file_path}")
            except ValueError:
                print(f"Skipping invalid file name: {file_name}")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

# 사용자 입력 받기
directory_path = input("Enter the directory path: ").strip()
attribute1 = input("Enter the attribute1 (e.g., ripe_yulgwa_1 or ripe_yulgwa_2): ").strip()
start = int(input("Enter the start number for attribute2 (e.g., 0 for 000000): ").strip())
end = int(input("Enter the end number for attribute2: ").strip())
new_class = int(input("Enter the new class number: ").strip())

# 클래스 정보 수정 실행
modify_class_by_attribute(directory_path, attribute1, start, end, new_class)
