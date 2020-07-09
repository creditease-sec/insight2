
def passwd_judge(passwd):
    advice = []

    if len(passwd) < 8:
        return "您的密码长度小于8，请重试!"

    result = [0, 0, 0, 0]
    for i in passwd:
        if sum(result) >=3:
            break
        else:
            if i.isupper():
                result[0] = 1
            elif i.islower():
                result[1] = 1
            elif i.isdigit():
                result[2] = 1
            else:
                result[3] = 1
    if sum(result) < 3:
        return "您的密码需要包括大写字母、小写字母、数字、其它符号,以上四种至少三种"


#print (passwd_judge("admin!xxx"))
#def passwd_judge3():
#    for a in range(len(passwd)-3):
#        if passwd.count(passwd[a:a + 3]) >=2:
#            print (passwd[a:a + 3])
#            advice.append("你的密码有长度超过或等于3的子串重复！")
#            break


