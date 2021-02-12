# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 10:03:34 2021

@author: Xabier
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Candidate():
    def __init__(self, ide, gender='M', n_absolute=3, categoricals=[2, 4, 3], rel_factor = 0.5):
        self.id = ide
        self.gender = gender
        
        # Absolute indicators from 0 to 1 (such as attractiveness, wealth, ...)
        # Common preference for the higher ones (most attractive, richer etc.)
        self.absolutes = np.random.rand(n_absolute)
        
        # Categorical indicators (race, religion, background)
        # Preference for the most self similar one (i.e. cat. 1 will prefer ONLY cat. 1)
        self.categories = []
        for c in categoricals:
            self.categories.append(np.random.randint(0, c))
        
        # Importance of absolutes vs. categoricals (0: only absolutes, 1: only categoricals)
        self.rel_factor = rel_factor
        
        # ** MATCHING indicators **
        self.preferences = []
        self.matched = False
        self.partner = None
        self.partner_value = 0

    def determine_preference(self, c):
        if c.gender != self.gender: # Prefer only opposite sex
            absolute = c.absolutes.mean()
            cat_bonus = 0
            for my_c, their_c in zip(self.categories, c.categories):
                if my_c == their_c:
                    cat_bonus += 1
            cat_bonus /= len(self.categories)
            
            return (1 - self.rel_factor) * absolute + self.rel_factor * cat_bonus
        else:
            return 0
    
    def make_match(self, c):
        self.partner = c.id
        self.matched = True
        self.partner_value = self.determine_preference(c)
        
        c.partner = self.id
        c.matched = True
        #c.partner_value.determine_preference(self)
    
    def break_match(self):
        self.partner = 0
        self.matched = False
    def __str__(self):
        return f"Candidate [{self.id}] : {self.gender} : {self.absolutes} / {self.categories}\n Matched: {self.matched} Partner: {self.partner}"

if __name__ == '__main__':
    n_males = 300
    n_females = n_males
    rel_factor = 0.7
    
    n_absolute=4
    categoricals=[2, 10, 4]
    
    males = {}
    females = {}
    for i in range(n_males):
        males[i] = Candidate(i, gender='M', rel_factor=rel_factor)
    for i in range(n_males, n_males + n_females):
        females[i] = Candidate(i, gender='F', rel_factor=rel_factor)
    
    # Precompute male preference matrices
    for m in males:
        male = males[m]
        attractiveness = {}
        for f in females:
            female = females[f]
            attractiveness[female.id] = male.determine_preference(female)
        attractiveness = sorted(attractiveness.items(), key=lambda x: x[1], reverse=True)
        male.preferences = [x[0] for x in attractiveness]
    
    # Perform matchmaking
    iter_data = []
    for i in range(400): # Iterations
        for m in males:
            male = males[m]
            if male.matched == False:  # Only if male is free make a proposal
                propose_to = male.preferences.pop(0)  # Get his next highest preference
                if females[propose_to].matched == False:  # If female is free make match...
                    females[propose_to].make_match(male)
                    male.partner_value = male.determine_preference(females[propose_to])
                else:  # ...else female decides if new proposal is better than current couple
                    new_value = females[propose_to].determine_preference(male)
                    if new_value > females[propose_to].partner_value:
                        # Remove the old partner
                        males[females[propose_to].partner].break_match()
                        females[propose_to].make_match(male)
                        male.partner_value = male.determine_preference(females[propose_to])
        
        # Compute iteration statistics
        matched = 0
        avg_male_val = 0
        avg_female_val = 0
        for m in males:
            if males[m].matched:
                matched += 1
                avg_male_val += males[m].partner_value
        for m in females:
            if females[m].matched:
                avg_female_val += females[m].partner_value
        
        data = {'matches': matched, 
                'avg_male_val': avg_male_val / len(males),
                'avg_female_val': avg_female_val / len(females)}
        iter_data.append(data)
                        
    
    # print
    for i in males:
        print(males[i])
    print("------------")
    for i in females:
        print(females[i])
    
    # Plot evolution
    
    res = pd.DataFrame(iter_data)
    fig, ax = plt.subplots(1,1)
    
    ax.set_title(f"Gale–Shapley match-making algorithm simulation\n {n_males} candidates, {n_absolute} absolute attributes\n {categoricals} categorical attribute distribution\n {(1 - rel_factor) * 100:.2f}% absolute importance")
    ax.plot(res["matches"], 'g--')
    twinx = plt.twinx(ax)
    twinx.plot(res["avg_male_val"])
    twinx.plot(res["avg_female_val"])
    ax.legend(["Matches"], loc=0)
    twinx.legend(["Avg. male value", "Avg. female value"], loc=3)
    ax.grid(True)
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Number of matches")
    twinx.set_ylabel("Value [0-1]")

    