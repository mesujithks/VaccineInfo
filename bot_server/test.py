from db import DBHelper

dataBase = DBHelper()

def main():
    dataBase.setup()
    print(dataBase.get_all_chat_id())
    


if __name__ == '__main__':
    main()