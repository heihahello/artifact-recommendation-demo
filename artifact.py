# >>> list(datas.iloc[2][3:]) 
# ['hydro=46.6%', 'e_m=19', 'def=12.4%', 'crit_dmg=20.2%', 'def=44']

class effect:
    """
    The class defining an effect, including its name, value_type(percent/num), 
    and bonus_value
    """
    def __init__(self, effect_str):
        """
        The constructor of effect class, set up basic info of an effect
        ---
        Parameter:
        effect_str: a string of effect, i.e.'hydro=46.6%'
        """
        #avoid case difference and clean extra space
        lower = effect_str.lower().strip()
        #set up the name of effect
        self.name  = lower[:lower.find('=')]
        #set up the value_type & bonus_value of effect
        if '%' in lower:
            self.value_type = 'percent'
            self.bonus_value = round(float(lower[lower.find('=') + 1 : -1]), 1)
        else:
            self.value_type = 'number'
            self.bonus_value = round(float(lower[lower.find('=') + 1:]), 1)

class artifact:
    """
    The class defining an artifact, including its unique serial_number, 
    set_kind, position, and effect_list.
    """
    def __init__(self, serial_number, position, set_kind, raw_effects):
        """
        The constructor of artifact class
        ---
        Parameter:
        serial_number: an int showing the unique number of every artifact
        set_kind: a string showing the name of this artifact's set i.e.'绝缘'
        position: a string shownig this artifact's position i.e.'羽'
        raw_effects: a list of strings of effects i.e.['雷=46.6%', 'atk=18.7%']
        """
        self.serial_number = serial_number
        self.set_kind = set_kind
        self.position = position
        #turn raw_effects list into a list of effect objects 
        self.effect_lst = [effect(to_add) for to_add in raw_effects]
        #print(self.effect_lst)

class artifact_set:
    """
    The class defining a set of artifacts, including the serial_numbers of 
    artifacts, and all effects in this set
    """
    def __init__(self, artifacts):
        """
        The constructor of artifact_set class
        ---
        Parameter:
        artifacts: a list of 5 artifact objects (as an artifact set)
        """
        #default 4-piece effect is none
        self.set4_effect = None
        #collect the kinds of artifact for calculating extra set2 & set4 effect
        self.kinds = [artifact.set_kind for artifact in artifacts]
        #sum up all unique serial numbers of artifacts in this set
        self.serial_numbers = ','.join([str(artifact.serial_number) 
            for artifact in artifacts])

        #sum up all effects in this set, including the set2 & set4 effects
        #i.e.[{'crit_dmg_percent': 112.0}, 13(none if no set4 effects)] 
        #note: this func only calculates set2 effect, set4 effect will be 
        #calculated by func calculate_artifacts in recommendation.py later
        self.effects = [self.sum_up_effects([effect for artifact in artifacts 
            for effect in artifact.effect_lst]), self.set4_effect]

    def set_effect(self):
        """
        this func active set2 or set4 effect by counting the set_kind of all
        artifacts in the set
        ---
        Return: a len 2 list with first element as a list of set2 effects and
        second element as a list of set_number which activates set4 effect 
        """
        #dict of all set2 effects with key as unique set_number and 
        # value as set2 effect
        set2_effect_dict = {
            1 : effect('atk=18%'), #余响
            2 : effect('dendro=15%'), #草套
            3 : effect('e_m=80'), #饰金
            4 : effect('hydro=15%'), #水套
            5 : effect('physical=25%'), #苍白
            6 : effect('electro=15%'), #平雷
            7 : effect('pyro=15%'), #魔女(火套)
            8 : effect('atk=18%'), #追忆
            9 : effect('physical=25%'), #骑士
            10 : effect('geo=15%'), #岩套
            11 : effect('shield=35%'), #逆飞
            12 : effect('pyro_res=40%'), #渡火
            13 : effect('e_r=20%'), #绝缘
            14 : effect('electro=15%'), #如雷
            15 : effect('def=30%'), #华馆
            16 : effect('heal=15%'), #海染
            17 : effect('e_m=80'), #乐团
            18 : effect('hp=20%'), #千岩
            19 : effect('atk=18%'), #角斗士
            20 : effect('cryo=15%'), #冰套
            21 : effect('dmg=20%'), #宗室
            22 : effect('anemo=15%'), #风套
            23 : effect('atk=18%'), #辰砂
            24 : effect('heal=15%'), #少女
            25 : effect('e_m=80'), #乐园
            26 : effect('anemo=15%'), #沙上楼阁
        }

        #count appearance of artifacts' sets
        kind_dict = {}
        for kind in self.kinds:
            if kind not in kind_dict:
                kind_dict[kind] = 1
            else:
                kind_dict[kind] += 1
        
        #activate the set2 effect when more than 2 artifacts from the same set 
        #exist in the set
        set2_effects = [set2_effect_dict[kind] for kind in kind_dict 
            if kind_dict[kind] >= 2]
        #put the set_number of the artifact set with more than 4 artifacts 
        #into a list
        set4_effect = [kind for kind in kind_dict if kind_dict[kind] >= 4]
        return [set2_effects, set4_effect]
    
    def sum_up_effects(self, raw_effects_lst):
        """
        this func sum
        ---
        Parameter:
        raw_effects_lst: a list of all effect objects
        Return: a dict of summary of all bonus from this artifact set, key as
        bonus name string and value as bonus value's float
        """
        info = {}
        #get the possible set effects
        set_effects= self.set_effect()

        #update the set4_effect with the unique number of this set if existing,
        #otherwise leave set4_effect be none
        if len(set_effects[1]) > 0:
            self.set4_effect = set_effects[1][0]

        #sum up all effects into info dict
        for effect in raw_effects_lst + set_effects[0]:
            #classify the percent and pure number bonus as different type
            if effect.value_type == 'percent':
                effect_key = effect.name + '_percent'
            else:
                effect_key = effect.name + '_number'
            #add up bonus with same type
            if effect_key not in info:
                info[effect_key] = round(effect.bonus_value, 1)
            else:
                info[effect_key] = round(info[effect_key] + effect.bonus_value,
                    1)
        return info

    def get_set_summary(self):
        """
        this func is return the information of this artifact set, including the
        artifacts and all bonuses, mainly for debug
        ---
        Return: a len 2 list with first element as a list of set2 effects and
        second element as a list of set_number which activates set4 effect 
        """
        return [self.serial_numbers, self.effects]
