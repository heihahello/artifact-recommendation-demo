import artifact as artifacts_setup
import pandas as pd

class recommendation:
    """
    The class is to make the recommendations
    """
    elements = ['anemo','pyro','geo','hydro','dendro','cryo','electro']
    def __init__(self, artifact_file, character_file):
        """
        The constructor of recommendation class, setting up the character info 
        and retriving the data from excel
        ---
        Parameter:
        filename: a string of excel form name
        character: a dict containing base value of character
        damage_dependence: a string of attribute which damage dealt depends on
        """
        #get artifact datas
        self.artifact_datas = pd.read_excel(artifact_file)
        print(self.artifact_datas)

        #get character infos
        raw_character = pd.read_excel(character_file)
        character_info = raw_character.set_index(list(raw_character)[0])
        self.character = character_info.to_dict()[list(character_info)[0]]
        self.damage_dependence = self.character.popitem()[1]



    def calculate_artifacts(self, effects):
        """
        this func calculate the expected value of damage of one artifact set
        as score
        ---
        Parameter:
        effects: a length 2 list containing the effect objects of an artifact 
        set. i.e.[{'crit_dmg_percent': 112.0}, 13] 
        Return:
        a float of score of this artifact set
        """
        #get the basic and set2 bonus of this artifact set
        basic = effects[0]
        #get the set4 effect, none if no set4 effect
        extra = effects[1]

        #calculate the elemental dmg bonus
        elemental_bonus = sum([basic[element + '_percent'] 
            for element in recommendation.elements 
                if element+'_percent' in basic])

        #calculate the basic dmg after adding up the bonuses on the dmg 
        #depending attribute
        try:
            basic_dmg = basic[self.damage_dependence + '_number'] + \
                (1 + basic[self.damage_dependence + '_percent']/100) * \
                    self.character[self.damage_dependence]
        except:
            basic_dmg = (basic[self.damage_dependence + '_number'] + \
                self.character[self.damage_dependence])

        #Ei(注：本部分为薙刀专用,可忽略 only for Engulfing Lightning weapon)
        # weapon_bonus = (basic['e_r_percent'] + self.character['e_r'] + 30 - \
        #   100) / 100 * 0.28
        # if weapon_bonus >= 0.8:
        #     basic_dmg += self.character[self.damage_dependence] * 0.8
        # else:
        #     basic_dmg += self.character[self.damage_dependence] *weapon_bonus
        
        #目前4件套效果(set4 effect)只制作了绝缘套(13)
        if extra == 13:
                Q_dmg_bonus = (basic['e_r_percent'] + self.character['e_r'] + \
                    30) * 0.25 / 100 + 1
                if Q_dmg_bonus >= 1.75:
                    Q_dmg_bonus = 1.75
                basic_dmg = basic_dmg * Q_dmg_bonus

        #calculate critical damage and non-critical damage
        crit_damage = basic_dmg * (1 + elemental_bonus / 100)\
            * (100 + basic['crit_dmg_percent'] + self.character['crit_dmg']) \
                / 100
        not_crit_damage = basic_dmg * (1 + elemental_bonus / 100)

        #calculate new critical rate
        try:
            new_crit_rate = basic['crit_rate_percent'] / 100 \
                + self.character['crit_rate'] / 100
        except:
            new_crit_rate = self.character['crit_rate'] / 100
        
        #calculate the expected value of dmg as the score of this artifact set
        score = crit_damage * new_crit_rate + \
            not_crit_damage * (1 - new_crit_rate)
        return score

    def generate_set(self):
        """
        this func generates all possible combination of artifact set from 
        artifact_datas
        ---
        Return:
        a dict of all set generated with key as artifacts' serial_numbers and 
        value as set's effects (i.e.[{'crit_dmg_percent': 112.0}, 13])
        """
        all_artifacts = {
            "circlect":[],
            "flower":[],
            "plume":[],
            "sands":[],
            "goblet":[]
        }
        
        #sort all artifacts by position from artifact_datas and put in 
        #all_artifacts dict with key of positions
        for i in range(self.artifact_datas.shape[0]):
            info = list(self.artifact_datas.iloc[i])
            #print(info)
            artifact_to_add = artifacts_setup.artifact(i, info[0], info[1], 
                info[2:])
            all_artifacts[artifact_to_add.position].append(artifact_to_add)

        #generate all sets and put in set_dict with set's effects
        set_dict = {}
        for circlect in all_artifacts["circlect"]:
            for flower in all_artifacts["flower"]:
                for plume in all_artifacts["plume"]:
                    for sands in all_artifacts["sands"]:
                        for goblet in all_artifacts["goblet"]:
                            new_set = artifacts_setup.artifact_set(
                                [circlect, flower, plume, sands, goblet])
                            set_dict[new_set.serial_numbers] = new_set.effects
        
        return set_dict

    def recommend(self, num_results):
        """
        this func recommends the artifact set with largest expected damage, 
        showing best of result based on how many you want to check, all results
        ranked in descending order
        ---
        Parameter:
        num_results: the number of result you want to see
        """
        #generate all artifact sets
        artifacts_set = self.generate_set()
        
        #calculate all set scores and sort them with score
        #(score, set)
        score_tuple_lst = [(self.calculate_artifacts(effects), set)
            for set, effects in artifacts_set.items()]
        score_tuple_lst.sort(reverse=True)

        #print the best results along with the new character info
        for i in range(num_results):
            print(score_tuple_lst[i][1])
            set = artifacts_set[score_tuple_lst[i][1]]

            #update the character attributes with the artifact bonuses
            new_character = {}
            for effect, value in self.character.items():
                new_value = value
                if effect == 'crit_rate' or effect == 'crit_dmg' or \
                    effect == 'e_r':
                    new_value += set[0][effect + '_percent']
                else:
                    if effect + '_percent' in set[0]:
                        new_value = round(new_value * (1 + \
                            set[0][effect + '_percent'] / 100))
                    if effect+'_number' in set[0]:
                        new_value = round(new_value + \
                            (set[0][effect + '_number']))
                new_character[effect] = new_value
            
            print(new_character)



##############################################################################
############################# start here #####################################
##############################################################################

#number of best results you want to check
num = 10

new_recommendation = recommendation('artifacts.xlsx', 'character.xlsx')
new_recommendation.recommend(num)
