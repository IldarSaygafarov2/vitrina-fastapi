import csv
import json
from pprint import pprint


def read_json(json_path: str) -> list[dict]:
    with open(json_path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def make_json(csv_path: str, json_path: str):
    data = []

    with open(csv_path, encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data.append(row)

    with open(json_path, mode="w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def clean_json(json_path: str, *fields):
    result = []

    content = read_json(json_path)
    categories = read_json("external/categories.json")
    districts = read_json("external/districts.json")
    users = read_json("external/users.json")
    gallery = read_json("external/api_advertisementgallery.json")

    categories = {i["id"]: i["name"] for i in categories}
    districts = {i["id"]: i["name"] for i in districts}
    users = {i["id"]: i["tg_username"] for i in users}
    # gallery = {i["advertisement_id"]: i["photo"] for i in gallery}
    imgs = {}
    for item in content:
        copied_item = item.copy()
        copied_item["images"] = []

        for key, value in item.items():
            if key in fields:
                copied_item.pop(key)
            if key == "category_id":
                copied_item[key] = categories[value]
            if key == "district_id":
                copied_item[key] = districts[value]
            if key == "user_id":
                copied_item[key] = users.get(value)

            if key == "id":
                imgs[item["name"]] = []
                for img in gallery:
                    if value == img["advertisement_id"]:
                        imgs[item["name"]].append(img)

        result.append(copied_item)

    with open("external/test.json", mode="w", encoding="utf-8") as t:
        json.dump(imgs, t, indent=4, ensure_ascii=False)

    return result


# districts = clean_json("external/districts.json", "name_ru", "id")
# categories = clean_json("external/categories.json", "name_ru", "id")
advertisements = clean_json("external/advertisements.json")
# pprint(advertisements)

# make_json("external/api_district.csv", "external/districts.json")
# make_json("external/api_category.csv", "external/categories.json")
# make_json("external/api_advertisement.csv", "external/advertisements.json")
# make_json("external/users_user.csv", "external/users.json")
# make_json(
#     "external/api_advertisementgallery.csv",
#     "external/api_advertisementgallery.json",
# )
