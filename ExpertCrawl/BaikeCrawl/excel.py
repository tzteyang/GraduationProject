import xlwt # 写入xls文件
import xlrd # 写入xls文件
import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent)
print(BASE_DIR)
sys.path.append(BASE_DIR)

def write_excel(data_list):
    """将数据文件内容写入excel
    Args:
        data_list (_list_): 数据文件的内容列表
    """
    # 创建新的workbook（其实就是创建新的excel）
    workbook = xlwt.Workbook(encoding= 'utf-8')

    # 创建新的sheet表
    worksheet = workbook.add_sheet("百度百科热词爬取结果")
    # 设置边框样式
    borders = xlwt.Borders()  # Create Borders

    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40

    style = xlwt.XFStyle()  # Create Style
    style.borders = borders  # Add Borders to Style
    
    # 表头
    heads = ['FIRST_INVENTOR', 'FIRST_PATENTEE', '类型', '我们的专利数量', '搜索的专利数量', '百度百科有', '论文的数量', '其他数据源']
    # 写表头
    for col in range(0,8):
        worksheet.write(0,col, heads[col], style)

    tmp_list = []
    tmp_list = data_list
    # 写表内容
    for row in range(len(tmp_list)):
        for col in range(len(tmp_list[row])):
            worksheet.write(row+1,col, tmp_list[row][col], style)
    # 保存
    workbook.save(BASE_DIR+"/scholar_result.xls")

def read_excel(excel_path):
    """将excel表中的内容存入数据文件
    Args:
        excel_path (_string_): excel文件的路径
    """
    data = xlrd.open_workbook(excel_path)
    table = data.sheets()[0]
    nrows = table.nrows
    data_list = []
    for row in range(nrows):
        if row == 0:
            continue
        tmp_list = []
        curr_len = table.row_len(row)
        for col in range(curr_len):
            tmp_list.append(table.cell_value(row,col))
        data_list.append(tmp_list)
    return tuple(data_list)



# data_list = list(jsonlines.open(BASE_DIR + "/output_en.jsonl"))
# write_excel(data_list)