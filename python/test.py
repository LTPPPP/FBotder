def split_text_by_star(text):
    # Tách đoạn văn bản thành các câu bằng cách sử dụng dấu chấm và dấu sao.
    sentences = text.split('*')
    
    # Loại bỏ khoảng trắng đầu và cuối của từng câu.
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    # Nối các câu lại với dấu xuống dòng.
    formatted_text = '\n'.join(sentences)
    
    return formatted_text

# Ví dụ sử dụng
input_text = """Công thức đạo hàm cơ bản: * Đạo hàm của hằng số: 0 * Đạo hàm của x^n: nx^(n-1), với n là một số thực bất kỳ * Đạo hàm của e^x: e^x * Đạo hàm của ln(x): 1/x * Đạo hàm của sin(x): cos(x) * Đạo hàm của cos(x): -sin(x) * Đạo hàm của tan(x): sec^2(x) * Đạo hàm của cot(x): -csc^2(x) * Đạo hàm của sec(x): sec(x)tan(x) * Đạo hàm của csc(x): -csc(x)cot(x) Invalid mathematical expression. Please provide a correct formula."""
output_text = split_text_by_star(input_text)
print(output_text)
