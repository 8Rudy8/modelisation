from math import *
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce



'''paramètres de modélisation'''

    #nombre de personnes à modéliser
EFFECTIF = 20
    #durée de la modélisation (en jours pour l'instant)
DUREE = 31 # on considère qu'on commence au début d'un cycle de x jours 
            #nb de modules
NB_MODULE = 20

CYCLE_FORAGE_LSR = 1#cycle de forage LSR (en jours)
CYCLE = [] #luminosité représentée par un chiffre entre O et 255
with open('cycle.txt','r') as fichiercycles :
    for l in fichiercycles :
        CYCLE.append(int(l.strip().split()[2])) 

    ##consommation d'eau potable par astronaute par jour ( en L )
V_EAU_J_P = 77.369

'''constantes de consommation (en kWh/j/pers)'''

    ## calcul de la consommation vis à vis des éclairages

        #plantation
            # surface de plantation supposée par personne  (en m²)
surface = 15
            #consommation de led en  W/m²
P_led_plantation_m2 = 180
            #consommation de la led pour un jour (en kWh)
conso_led_plante_j_p = surface * P_led_plantation_m2 *24*0.001

        #éclairage dans les modules
            #rayon intérieur du cylindre (module) (en m)
R_module = 2
            #longueur d'un module (en m)
L_module = 17
            #largeur de la surface au sol d'un module (en m)
l_sol_module = 2*sqrt(R_module**2 - (R_module-1.3)**2)
            #surface au sol d'un module (en m²)
S_sol_module = L_module * l_sol_module
            # 1 LED de ~10 W pour 5m² de sol donc 2W/m²
P_led_m2 = 2
            # conso d'éclairage par jour, si on suppose que toute la base est allumée (en kWh/ j)
conso_led_modules = P_led_m2*NB_MODULE*S_sol_module*24*0.001

    ##calcul de la consommation des procédés de recyclage

        # recyclage de l'urine
            #quantité d'urine par jour par personne (en L)
Ur_j_p = 1.8
            #pourcentage volumique d'eau dans l'urine (pas d'unité)
pvol_eau_urine = 0.95
            #rendement de l'extraction d'eau dans l'urine (pas d'unité)
r_recycl_urine = 0.9
            #volume d'eau obtenu par jour par personne (en L/j/pers)
V_eau_urine_j_p = Ur_j_p * pvol_eau_urine * r_recycl_urine
            #énergie spécifique d'évaporation ( <=> énergie conversion de l'eau ) (en kWh/L)
E_evap = 2.97
            #énergie utilisée pour recycler l'urine journalière d'une personne en kWh/pers
conso_recyclage_urine_j_p = V_eau_urine_j_p * E_evap
        #recyclage de l'air (ECLSS)  
            #  TO DO

    ## calcul consommation des systèmes ISRU
    
        #extraction de l'eau par forage LSR
            #consommation énergétique par L d'eau extrait (en kWh/L)
eff_foreuse = 8.6
            #vitesse d'extraction (en L/j)
v_extraction = 108
            #on en déduit la puissance d'une foreuse (en W)
P_foreuse = ((eff_foreuse*(10)**3)*3600)*(v_extraction/(3600*24))
            #volume d'extraction nécessaire pour atteindre avoir la quantité d'eau nécessaire (L/j/pers)
V_manquant_j_p =  V_EAU_J_P - V_eau_urine_j_p
            # énergie dépensée par jour par personnne pour atteindre ce volume (en kWh/j/pers)
conso_foreuse_LSR_j_p = V_manquant_j_p * eff_foreuse

            #énergie consommée le jour de forage:
conso_foreuse_p = conso_foreuse_LSR_j_p * CYCLE_FORAGE_LSR

    ##calcul de la consommation du système de chauffage
        #consommation par module (en W)
chauf_module_j = 834
        #consommation journalière (en kWh/pers/j)
chauf_module_jour = 62 * 24 * 0.001

'''fonctions de modelisation en fonction du temps'''

assert V_EAU_J_P <= V_eau_urine_j_p + V_manquant_j_p

def conso_jour_nuit(t,conso_jour,conso_nuit,seuil = 100):
    luminosite = CYCLE[t%len(CYCLE)]
    if luminosite > seuil :
        return conso_jour
    else :
        return conso_nuit
def modele_foreuse_LSR(t):
   
    jour_cycle = t%(CYCLE_FORAGE_LSR+1) #pour ne pas dépasser le cycle
    if jour_cycle == CYCLE_FORAGE_LSR : #si on est le dernier jour du cycle
        return conso_foreuse_p*EFFECTIF
    
    return 0
'''création et courbes'''

plt.figure(figsize=(13,8)) #ajuster la taille de la fenêtre

T = np.array(list(i for i in range(1,DUREE+1))) # représenter le temps 

consos=[]
Conso_eclairage_plante = np.array(list(map(lambda x : conso_led_plante_j_p*EFFECTIF,T))) #consommation éclairage alimentation
consos.append(Conso_eclairage_plante)
Conso_eclairage_modules = np.array(list(map(lambda t : conso_jour_nuit(t,conso_led_modules,conso_led_modules*1.2),T))) #consommation éclairage alimentation
consos.append(Conso_eclairage_modules)
Conso_urine = np.array(list(map(lambda x : conso_recyclage_urine_j_p*EFFECTIF,T))) # consommation du recyclage de l'urine
consos.append(Conso_urine)
Conso_chauffage = np.array(list(map(lambda x : chauf_module_jour*NB_MODULE,T))) # consommation du chauffage de la base
consos.append(Conso_chauffage)
Conso_foreuse_LSR = np.array(list(map(lambda t : modele_foreuse_LSR(t),T))) #consommation de la foreuse LSR
consos.append(Conso_foreuse_LSR)

Conso_eclairage = Conso_eclairage_modules + Conso_eclairage_plante

conso_tot = sum(consos) # consommation totale

max_eclairage = format(max(Conso_eclairage),'.1f')
max = format(max(conso_tot),'.1f')

plt.plot(T,conso_tot)
plt.plot(T,Conso_eclairage,'')
plt.plot(T,Conso_urine)
plt.plot(T,Conso_chauffage)
plt.plot(T,Conso_foreuse_LSR,'r+')

'''affichage des courbes'''

plt.legend(
    ["totale","éclairage (max "+ str(max_eclairage)+" kWh/j)","recyclage urine ("+ str(format(Conso_urine[0],'.1f'))+" kWh/j)","contrôle thermique ("+ str(format(Conso_chauffage[0],'.1f'))+" kWh/j)","Foreuses LSR"],
    loc='upper right',
   title="pics d'énergie : "+ str(max)+" kWh"
  )
plt.xlabel('Temps (en jour)')
plt.ylabel('Consommmation électrique (en kWh)')
plt.title('Consommation électrique de la base lunaire en fonction du jour')
plt.show()
