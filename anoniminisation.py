import pandas as pd

filename = 'dataset1m.xlsx'  # <- filename
df = pd.read_excel(filename)

# Flags
ANONIMIZE_JOBS = True
ANONIMIZE_ADDRESS = True
ANONIMIZE_SALARY = True
DELETE_RARE_ATTRIBUTES = True
SAVE_ANON_FILE = False


def f1(x):
    val = int(x)
    if val > 100000:
        return "Very high"
    elif val > 75000:
        return "High"
    elif val > 55000:
        return "Mid"
    else:
        return "Low"


def f2(x):
    return '***'


def f3(x):
    return x.split(" д. ")[0]


if ANONIMIZE_SALARY:
    df["Заработная плата"] = df["Заработная плата"].apply(f1)

# ФИО - прямой идентефикатор - всегда анонимизируем
df["ФИО работника"] = df["ФИО работника"].apply(f2)

if ANONIMIZE_ADDRESS:
    df["Адрес работы"] = df["Адрес работы"].apply(f3)


# %%
def func(x):
    s = str(x)
    if x == "Генеральный директор":
        return "*"
    elif x == "Секретарь" or x == "Бухгалтер":
        return "*"
    elif x == "Административный директор" or x == "Директор по маркетингу" or x == "Финансовый директор":
        return "Директор"
    elif x == "Водитель" or x == "Комендант" or x == "Охранник" or x == "Уборщик":
        return "Вспомогательный персонал"
    else:
        return s


if ANONIMIZE_JOBS:
    df["Должность"] = df["Должность"].apply(func)

def func(x):
    s = str(x)
    if s == "*":
        return s
    elif int(s[1:4]) in [929, 921, 931]:
        return "Megafon"
    elif int(s[1:4]) in [911, 981]:
        return "MTS"
    elif int(s[1:4]) in [961, 962, 963, 964, 903, 905, 906, 909, 960]:
        return "Beeline"
    elif int(s[1:4]) in [901, 952, 904, 950, 951]:
        return "Tele2"


# Прямой идентефикатор - всега анонимизируем
df["Номер телефона"] = df["Номер телефона"].apply(func)


def get_dict_and_k_anonimity():
    mydictionary = {}

    def getstrline(index):
        return str(df["ФИО работника"].iloc[index]) + str(df["Номер телефона"].iloc[index]) + str(
            df["Адрес работы"].iloc[index]) + str(df["Должность"].iloc[index]) + str(df["Заработная плата"].iloc[index])

    for i in range(df.shape[0]):
        s = getstrline(i)
        if s in mydictionary:
            mydictionary[s] += 1
        else:
            mydictionary[s] = 1
    return mydictionary, min(mydictionary.values())


mydict, k_anoninity = get_dict_and_k_anonimity()
print("K-anon before deletion = ", k_anoninity)

sorted_mydict = sorted(mydict.items(), key=lambda x: x[1])
for i in range(5):
    print(sorted_mydict[i])

df.astype(str).values.flatten().tolist()
r = [''.join(val) for val in df.astype(str).values.tolist()]

index = 0
forDelete = []

for index in range(df.shape[0]):
    line = r[index]
    if mydict[line] < 5:
        # print(line, ">>", index)
        forDelete.append(index)
    index += 1
print(len(forDelete), " lines need to be deleted to meet all requirements")

if DELETE_RARE_ATTRIBUTES:
    df = df.drop(df.index[forDelete])

newdict, new_k_anonimity = get_dict_and_k_anonimity()
print("After correction new k-anon = ", new_k_anonimity)

sorted_newdict = sorted(newdict.items(), key=lambda x: x[1])
for i in range(5):
    print(sorted_newdict[i])

path = filename.split('.')[0] + 'anonymized.xlsx'

if SAVE_ANON_FILE:
    df.to_excel(path, index=False)
