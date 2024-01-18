
import os
import json

class LBAL:
    def __init__(self):
        self.filename = os.path.join(os.getenv('APPDATA'), r"Godot\app_userdata\Luck be a Landlord\LBAL.save")
        self.save_last_time = 0
        self.symbols = json.load(open("symbols.json", "r"))
        self.items = json.load(open("items.json", "r"))
        self.essences = json.load(open("essences.json", "r"))
        self.all = {}
        for i in self.symbols: self.all[i] = self.symbols[i]
        for i in self.items: self.all[i] = self.items[i]
        for i in self.essences: self.all[i] = self.essences[i]
        self.build_map()
        self.queued_increase = 0
        self.prevgold = 0

    def update(self):
        j = []
        os.system("cls")
        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                for i in range(12):
                    j.append(json.loads(f.readline()))
            except Exception as e:
                print(e)
                return
        
        self.gold = j[3]["coins"] + j[3]["queued_increase"]
        info = j[11]
        due, rolls = info["rent_values"]
        self.floor = info["current_floor"]
        self.removal = info["removal_tokens"]
        self.reroll  = info["reroll_tokens"]
        self.cur_symbols = []
        for i in range(4,9): self.cur_symbols.extend(j[i]["icon_types"])
        self.cur_items = j[9]["item_types"]
        for itm in j[9]["destroyed_item_types"]:
            avail = self.all[itm].get("active_in_discard", True)
            if avail: self.cur_items.append(itm)

        for k in range(len(self.cur_items)):
            itm = self.cur_items[k]
            if itm.endswith("_d"): itm = itm[:-2]; self.cur_items[k] = itm
        self.cur_all = self.cur_symbols + self.cur_items

        self.choices = info["saved_card_types"]
        self.taken = info["taken"]
        spins = info["spins"]
        spinsleft = 15-(spins-1)%15
        self.queued_increase = self.queued_increase or 0
        self.prevgold = self.prevgold or 1
        if(len(self.choices)>0 and self.prevgold != self.gold):
            self.queued_increase = self.gold - self.prevgold
            self.prevgold = self.gold

        print(f"Gold: {self.gold} ( + {self.queued_increase} * {rolls} = {self.gold+self.queued_increase*rolls} )\nDue: {due}   ({self.gold+self.queued_increase*rolls-due} left after pay)")
        print(f"Count of Symbols: {len(self.cur_symbols)-self.cur_symbols.count('empty')} (Add 1 Dud in {spinsleft} turns)")
        self.check_removal()
        self.check_add()

    def check_removal(self):
        if self.removal == 0: return
        print("Remove symbols!")

    def check_add(self):
        if not self.choices: return
        for itm in self.choices:
            count = self.cur_all.count(itm)
            if count==0:
                print(f"-----------{itm}-----------")
            else: 
                print(f"-----------{itm}({count})-----------")
            if count>=2:
                used_itms = []
                for itm2 in self.cur_items:
                    if itm2 in used_itms: continue
                    count3 = self.all[itm2].get("count3", False)
                    if itm2.endswith("_essence"):
                        ie = itm2[:-8]
                        count3 = self.all[itm2].get("count3", self.all[ie].get("count3", False))
                    if count3:
                        count = self.cur_items.count(itm2)
                        if count>1:
                            print(f"    {itm2}({count})")
                        else:
                            print(f"    {itm2}")
                        used_itms.append(itm2)
            
            for l, c in self.all[itm].get("clinks", []):
                if c in self.cur_all and l in self.cur_all:
                    count = self.cur_all.count(l)
                    if(count==1): print(f"    {l}    {c}")
                    else: print(f"    {l}({count})    {c}")
            for l in self.all[itm].get("links", []):
                if l in self.cur_all:
                    count = self.cur_all.count(l)
                    if(count==1): print(f"    {l}")
                    else: print(f"    {l}({count})")
            count3 = self.all[itm].get("count3", False)
            if itm.endswith("_essence"):
                ie = itm[:-8]
                count3 = self.all[itm].get("count3", self.all[ie].get("count3", False))
            if count3:
                list3 = []
                for it in self.cur_symbols:
                    z = [x for x, y in list3]
                    if it == "empty" or it in z: continue
                    count = self.cur_symbols.count(it)
                    if count>1: list3.append((it,count))
                list3.sort(key=lambda x: x[1], reverse=True)
                for l, c in list3:
                    print(f"    {l}({c})")
    
    def build_map(self):
        self.groups = {}
        for i in self.all:
            groups = self.all[i].get("groups", [])
            for g in groups: 
                if not g in self.groups:
                    self.groups[g] = []
                self.groups[g].append(i)
        
        for i in self.all:
            linki = self.all[i].get("linki", [])
            linkg = self.all[i].get("linkg", [])
            linkcg = self.all[i].get("linkcg", [])
            if i.endswith("_essence"):
                ie = i[:-8]
                linki = self.all[i].get("linki", self.all[ie].get("linki", []))
                linkg = self.all[i].get("linkg", self.all[ie].get("linkg", []))
                linkcg = self.all[i].get("linkcg", self.all[ie].get("linkcg", []))

            for j in linki:
                self.add_link(i, j)
            for g in linkg: 
                for j in self.groups[g]: 
                    self.add_link(i, j)
            if linkcg:
                c, g = linkcg
                for j in self.groups[g]: 
                    self.add_clink(i, j, c)
        
        for i in self.all:
            if i.endswith("_essence"): i=i[:-8]
            addi = self.all[i].get("addi", [])
            addg = self.all[i].get("addg", [])
            if i.endswith("_essence"):
                ie = i[:-8]
                addi = self.all[i].get("addi", self.all[ie].get("addi", []))
                addg = self.all[i].get("addg", self.all[ie].get("addg", []))
            for g in addg:
                for k in self.groups[g]: 
                    addi.append(k)
            for jj in addi:
                for j in self.all[jj].get("links", []):
                    self.add_link(i, j)
                for j,c in self.all[jj].get("clinks", []):
                    self.add_clink(i,j,c)
            
    def add_link(self, i, j):
        if not self.all[i].get("links"): self.all[i]["links"] = []
        if not j in self.all[i]["links"]: 
            self.all[i]["links"].append(j)
        if not self.all[j].get("links"): self.all[j]["links"] = []
        if not i in self.all[j]["links"]: self.all[j]["links"].append(i)

    def add_clink(self, i, j, c):
        if not self.all[i].get("clinks"): self.all[i]["clinks"] = []
        self.all[i]["clinks"].append((j,c))
        if not self.all[j].get("clinks"): self.all[j]["clinks"] = []
        self.all[i]["clinks"].append((i,c))

    def run(self):
        while(True):
            last_time = os.path.getmtime(self.filename)
            if last_time > self.save_last_time : 
                self.save_last_time = last_time
                self.update()

if __name__  == "__main__":
    lbal = LBAL()
    lbal.run()