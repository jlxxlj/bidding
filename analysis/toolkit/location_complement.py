# coding=utf-8
# author="Jianghua Zhao"
import re
import json
from collections import OrderedDict
import os

current_folder = os.path.dirname(os.path.abspath(__file__))


def read_nationality():
    with open(os.path.join(current_folder, "location_complement_data/nationality.txt")) as f:
        txt = f.read()
        txt = txt.decode("utf-8")
        items = txt.split(u"、")
        tmp = [it[:-1] for it in items if len(it) > 3]
        items += tmp
        return items

nations = [u"汉族", u"蒙古族", u"回族", u"藏族", u"维吾尔族", u"苗族", u"彝族", u"壮族", u"布依族", u"朝鲜族", u"满族", u"侗族",
           u"瑶族", u"白族", u"土家族", u"哈尼族", u"哈萨克族", u"傣族", u"黎族", u"僳僳族", u"佤族", u"畲族", u"高山族",
           u"拉祜族", u"水族", u"东乡族", u"纳西族", u"景颇族", u"柯尔克孜族", u"土族", u"达斡尔族", u"仫佬族", u"羌族",
           u"布朗族", u"撒拉族", u"毛南族", u"仡佬族", u"锡伯族", u"阿昌族", u"普米族", u"塔吉克族", u"怒族", u"乌孜别克族",
           u"俄罗斯族", u"鄂温克族", u"德昂族", u"保安族", u"裕固族", u"京族", u"塔塔尔族", u"独龙族", u"鄂伦春族", u"赫哲族",
           u"门巴族", u"珞巴族", u"基诺族", u"傈僳族", u"维吾尔", u"哈萨克", u"柯尔克孜", u"达斡尔", u"塔吉克", u"乌孜别克",
           u"俄罗斯", u"鄂温克", u"塔塔尔", u"鄂伦春"]
re_nations = re.compile(u"|".join(nations))
re_suffix_new = re.compile(u"(?:自治)?(?:省|区|市|州|地区|盟|县|新?区|旗|群岛的岛礁及其海域|群岛|特别行政区)$")
re_suffix = re.compile(u"(?:自治)?(?:省|区|市|州|地区|盟|县|区|旗|群岛的岛礁及其海域|群岛|特别行政区)$")


def get_keyword(address):
    address_keyword = re_suffix_new.sub(u"", address)
    if len(address_keyword) < 2:
        address_keyword = re_suffix.sub(u"", address)
    address_keyword = re_nations.sub(u"", address_keyword)
    if len(address_keyword) < 2:
        address_keyword = address
    return address_keyword


def tokenize_region_name(region_name):
    tokens = [region_name]
    # 长度小于3的直接返回
    if len(region_name) < 3:
        return tokens

    if region_name.endswith(u"新区") and len(region_name) >= 4:
        suffix = u"新区"
        prefix = region_name[:-2]
    else:
        suffix = re_suffix.findall(region_name)
        suffix = suffix[0] if suffix else u""
        prefix = region_name[:len(region_name) - len(suffix)]

    # 去掉民族
    t_p = re_nations.sub(u"", prefix)
    if len(t_p) >= 2:
        tokens.append(t_p + suffix)

    # 去掉新
    t_sf = re.sub(u"新", u"", suffix)
    if len(t_p) >= 2:
        tokens.append(t_p + t_sf)
    if len(prefix) >= 2:
        tokens.append(prefix + t_sf)

    # 去掉联合
    t_sf = re.sub(u"联合", u"", suffix)
    if len(t_p) >= 2:
        tokens.append(t_p + t_sf)
    if len(prefix) >= 2:
        tokens.append(prefix + t_sf)

    # 去掉自治
    t_sf = re.sub(u"自治", u"", suffix)
    if len(t_p) >= 2:
        tokens.append(t_p + t_sf)
    if len(prefix) >= 2:
        tokens.append(prefix + t_sf)

    # 去掉后缀
    if len(t_p) >= 2:
        tokens.append(t_p)
    if len(prefix) >= 2:
        tokens.append(prefix)

    tokens.append(get_keyword(region_name))

    if region_name.startswith(u"内蒙古"):
        tokens.append(u"内蒙")

    if region_name.endswith(u"自治区"):
        tokens.append(get_keyword(region_name) + u"省")

    tokens = sorted(list(set(tokens)), key=lambda x: len(x))

    return tokens


class TireDict:
    def __init__(self, words=None, file_path=None):
        if isinstance(words, list) and words:
            self.words = words
        elif isinstance(file_path, basestring) and file_path:
            self.file_path = file_path
            self.load_words_from_file()
        else:
            self.words = []

        self.tire_root = [{}, False]
        self.initialize()

    def load_words_from_file(self):
        pass

    def add_words(self, words):
        self.words += words
        self.initialize()

    def initialize(self):
        self.tire_root = [{}, False]

        for word in self.words:
            tmp = self.tire_root
            for char in word:
                if char not in tmp[0]:
                    tmp[0][char] = [{}, False]
                tmp = tmp[0][char]
            tmp[1] = True

    def seg_sentence(self, sentence, stop=False):
        words = []

        tire_tmp = self.tire_root
        pre_state, cur_state = None, None
        idx = 0
        while len(sentence) > 0:
            char = sentence[idx]
            flag = False
            if char in tire_tmp[0]:
                flag = True
                if idx == 0:
                    cur_state = [0, ""]
                cur_state[0] = idx
                cur_state[1] += char
                tire_tmp = tire_tmp[0][char]
                if tire_tmp[1] is True:
                    if not pre_state:
                        pre_state = [0, ""]
                    pre_state[0] = cur_state[0]
                    pre_state[1] += cur_state[1]
                    cur_state[1] = ""
                idx += 1

            if flag is False or idx == len(sentence) > 0:
                if not pre_state:
                    if stop:
                        break
                    words.append(sentence[0])
                    sentence = sentence[1:]
                else:
                    words.append(pre_state[1])
                    sentence = sentence[pre_state[0] + 1:]
                tire_tmp = self.tire_root
                pre_state, cur_state = None, None
                idx = 0

        return words


class RegionLevel:
    REGION_LEVEL_MAP = {"nation": 0, "province": 1, "city": 2, "county": 3}

    def __init__(self):
        items = self.REGION_LEVEL_MAP.items()
        self.level_name = [it[0] for it in items]
        self.region_level = [it[1] for it in items]

    def get_level_name(self, level):
        if level in self.region_level:
            idx = self.region_level.index(level)
            return self.level_name[idx]
        else:
            return "undefined level %s" % level

    def get_region_level(self, level_name):
        region_level = self.REGION_LEVEL_MAP.get(level_name)
        if region_level is None:
            return -1
        return region_level


class RegionNode(object):
    def __init__(self, region_level=-1, region_name=u"未知", sub_regions=None):
        if sub_regions is None:
            sub_regions = []
        self.level_name = RegionLevel().get_level_name(region_level)
        self.region_name = region_name
        self.region_short_name = get_keyword(region_name)

        self.sub_regions = []
        self.sub_regions += sub_regions

        self.search_key_map = OrderedDict()
        tokens = tokenize_region_name(region_name)
        for token in tokens:
            self.search_key_map[token] = -1

        self._generate_search_key()

    def _generate_search_key(self):
        sub_search_key_map = OrderedDict()
        find_sub_region_search_key = {}
        for i, region in enumerate(self.sub_regions):
            find_sub_region_search_key[i] = False
            key_map = region.search_key_map
            for k in key_map.keys():
                if k in self.search_key_map:
                    continue
                if k not in sub_search_key_map:
                    sub_search_key_map[k] = []
                sub_search_key_map[k] += [i]

        # 去掉在同一级重复的检索关键字
        del_keys = []
        for k, v in sub_search_key_map.items():
            if len(v) > 1:
                levels = [self.sub_regions[sub_reg_idx].get_key_level(k) for sub_reg_idx in v]
                min_level = min(levels)
                if len([t for t in levels if t == min_level]) == 1:
                    idx = levels.index(min_level)
                    v = [v[idx]]
                else:
                    del_keys.append(k)
                    continue
            sub_search_key_map[k] = v[0]
            if self.sub_regions[sub_search_key_map[k]].search_key_map[k] == -1:
                find_sub_region_search_key[sub_search_key_map[k]] = True
        for key in del_keys:
            del sub_search_key_map[key]

        for sub_region_idx, is_find in find_sub_region_search_key.items():
            if is_find is False:
                print "Cannot find region_search_tree_old.json search key of the sub region(%s)" % self.sub_regions[sub_region_idx].region_name
        self.search_key_map.update(sub_search_key_map)

    def search_region(self, key_list):
        if isinstance(key_list, list) and len(key_list) > 0:
            if key_list[0] in self.search_key_map:
                idx = self.search_key_map[key_list[0]]
                if idx == -1:
                    if len(key_list) > 1:
                        region = self.search_region(key_list[1:])
                        if region:
                            return region
                    return {self.level_name: self.region_name}
                else:
                    region = OrderedDict({self.level_name: self.region_name})
                    sub_region = self.sub_regions[idx].search_region(key_list)
                    region.update(sub_region)
                    return region
        return None

    def get_key_level(self, key):
        level_name = None
        region = self.search_region([key])
        if region:
            level_name = region.keys()[-1]
        return RegionLevel().get_region_level(level_name)

    def get_region_node_dict(self):
        data = OrderedDict()
        data["levelName"] = self.level_name
        data["regionName"] = self.region_name
        data["regionShortName"] = self.region_short_name
        data["searchKeyMap"] = self.search_key_map
        data["subRegions"] = [reg.get_region_node_dict() for reg in self.sub_regions]
        return data

    def set_region_node_dict(self, data):
        self.level_name = data.get("levelName")
        self.region_name = data.get("regionName")
        self.region_short_name = data.get("regionShortName")
        self.search_key_map = data.get("searchKeyMap")
        self.sub_regions = []
        for region in data.get("subRegions"):
            reg_node = RegionNode()
            reg_node.set_region_node_dict(region)
            self.sub_regions.append(reg_node)


class RegionSearchTree:
    def __init__(self, region_data_file=None):
        self.region_data_file = region_data_file
        self.search_tree = self._generate_region_tree()
        self.search_keywords = None

    def _read_address(self):
        if self.region_data_file is None:
            return OrderedDict()
        with open(self.region_data_file, "r") as fo:
            result = OrderedDict()
            for line in fo.readlines():
                line = line.strip().decode("utf-8")
                items = line.split(",")
                items = [it.strip() for it in items]
                tmp_dict = result
                for i in range(len(items)):
                    if items[i] not in tmp_dict:
                        tmp_dict[items[i]] = {}
                    tmp_dict = tmp_dict[items[i]]
            return result

    @staticmethod
    def _create_region_search_tree(dic, level):
        regions = []
        if not isinstance(dic, dict):
            print "is not region_search_tree_old.json dict"
            return []
        for k, v in dic.items():
            sub_regions = []
            if v:
                if k in (u"北京市", u"上海市", u"天津市", u"重庆市"):
                    sub_regions = RegionSearchTree._create_region_search_tree(v, level + 2)
                else:
                    sub_regions = RegionSearchTree._create_region_search_tree(v, level + 1)
            node = RegionNode(level, k, sub_regions)
            regions.append(node)
        return regions

    def _generate_region_tree(self):
        address = self._read_address()
        address = {u"中国": address}
        region_tree = RegionSearchTree._create_region_search_tree(address, 0)[0]
        return region_tree

    @staticmethod
    def _get_all_search_keywords(region_node):
        keywords = []
        keywords += region_node.search_key_map.keys()
        for sub_region in region_node.sub_regions:
            keywords += RegionSearchTree._get_all_search_keywords(sub_region)
        return list(set(keywords))

    def _word_segment(self, sentence):
        if not self.search_keywords:
            search_keywords = RegionSearchTree._get_all_search_keywords(self.search_tree)
            self.search_keywords = sorted(search_keywords, key=lambda x: len(x), reverse=True)
            self.td = TireDict(words=self.search_keywords)
        key_list = self.td.seg_sentence(sentence, stop=True)
        return key_list

    def search(self, search_word):
        parts = re.findall(u"[\u4e00-\u9fa5]+", search_word)
        search_word = u"".join(parts)
        key_list = self._word_segment(search_word)
        return self.search_tree.search_region(key_list)

    def load(self, path):
        with open(path, "r") as f:
            region_tree = f.read().decode("utf-8")
            region_tree_dict = json.loads(region_tree)
            self.search_tree = RegionNode()
            self.search_tree.set_region_node_dict(region_tree_dict)

    def save(self, path):
        region_tree = self.search_tree.get_region_node_dict()
        with open(path, "w") as f:
            region_tree = json.dumps(region_tree, indent=4).decode("unicode-escape")
            f.write(region_tree.encode("utf-8"))


def get_full_region_name(dic):
    full_region_name = u""
    if isinstance(dic, dict):
        for level in range(1, 4):
            level_name = RegionLevel().get_level_name(level)
            if dic.get(level_name):
                full_region_name += dic.get(level_name)
    return full_region_name


def get_region_max_level(dic):
    max_level = 0
    if isinstance(dic, dict):
        for level in range(1, 4):
            level_name = RegionLevel().get_level_name(level)
            if dic.get(level_name):
                max_level = level
    return max_level


# address_data_path = os.path.join(current_folder, "location_complement_data/address_data.txt")
# REGION_SEARCH_TREE = RegionSearchTree(region_data_file=address_data_path)
# REGION_SEARCH_TREE.save(os.path.join(current_folder, "location_complement_data/region_search_tree.json"))
REGION_SEARCH_TREE = RegionSearchTree()
REGION_SEARCH_TREE.load(os.path.join(current_folder, "location_complement_data/region_search_tree.json"))


def search_full_region(search_word):
    return REGION_SEARCH_TREE.search(search_word)


if __name__ == "__main__":
    res = search_full_region(u"内蒙包头")
    print get_full_region_name(res)



