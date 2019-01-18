# -*- coding: utf-8 -*-

import os
import random
from json import load
import numpy
from csv import DictWriter
import deap
from deap import base, creator, tools, algorithms
from tee import retiraRepetido
#from . import BASE_DIR
#from .utils import makeDirsForFile, exist



def pmx(ind1, ind2):
    size = min(len(ind1), len(ind2))
    cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))
    temp1 = ind1[cxpoint1:cxpoint2+1] + ind2
    temp2 = ind1[cxpoint1:cxpoint2+1] + ind1
    ind1 = []
    for x in temp1:
        if x not in ind1:
            ind1.append(x)
    ind2 = []
    for x in temp2:
        if x not in ind2:
            ind2.append(x)
    return ind1, ind2

def ind2route(individual, instance):
    route = []
    vehicleCapacity = instance['vehicle_capacity']
    deportDueTime =  instance['deport']['due_time']
    # Initialize a sub-route
    subRoute = []
    vehicleLoad = 0
    elapsedTime = 0
    lastCustomerID = 0
    subRouteTotalTime = 0
    for customerID in individual:
        customerIDIndex = individual.index(customerID)
        # Update vehicle load
        demand = instance['customer_%d' % customerID]['demand']
        updatedVehicleLoad = vehicleLoad + demand
        # Update elapsed time
        serviceTime = instance['customer_%d' % customerID]['service_time']
        returnTime = instance['distance_matrix'][customerID][0]
        updatedElapsedTime = elapsedTime + instance['distance_matrix'][lastCustomerID][customerID] + serviceTime + returnTime
        # Validate if the vehicle can go to the next customer
        subRouteTotalTime += instance['distance_matrix'][customerID][customerIDIndex + 1]
        nextCustomerDueTime = instance['customer_%d' % (customerIDIndex + 1)]['due_time']
        # Validate vehicle load and time
        if (updatedVehicleLoad <= vehicleCapacity) and (updatedElapsedTime <= deportDueTime) and (subRouteTotalTime <= nextCustomerDueTime):
            # Add to current sub-route
            subRoute.append(customerID)
            vehicleLoad = updatedVehicleLoad
            elapsedTime = updatedElapsedTime - returnTime
        else:
            # Save current sub-route
            route.append(subRoute)
            # Initialize a new sub-route and add to it
            subRoute = [customerID]
            vehicleLoad = demand
            subRouteTotalTime = 0
            elapsedTime = instance['distance_matrix'][0][customerID] + serviceTime
        # Update last customer ID
        lastCustomerID = customerID
    if subRoute != []:
        # Save current sub-route before return if not empty
        route.append(subRoute)
    return route


def printRoute(txt, route, merge=False):    
    routeStr = '0'
    subRouteCount = 0
    for subRoute in route:
        subRouteCount += 1
        subRouteStr = '0'
        for customerID in subRoute:
            subRouteStr = subRouteStr + ' - ' + str(customerID)
            routeStr = routeStr + ' - ' + str(customerID)
        subRouteStr = subRouteStr + ' - 0'
        if not merge:
            txt.write('  Vehicle %d\'s route: %s' % (subRouteCount, subRouteStr))
            txt.write('\n')
        routeStr = routeStr + ' - 0'

    if merge:
        print(routeStr)
    
    return


def evalVRPTW(individual, instance, unitCost=1.0, initCost=0, waitCost=0):
    totalCost = 0
    route = ind2route(individual, instance)
    totalCost = 0
    for subRoute in route:
        subRouteTimeCost = 0
        subRouteDistance = 0
        elapsedTime = 0
        lastCustomerID = 0
        for customerID in subRoute:
            # Calculate section distance
            distance = instance['distance_matrix'][lastCustomerID][customerID]
            # Update sub-route distance
            subRouteDistance = subRouteDistance + distance
            # Calculate time cost
            arrivalTime = elapsedTime + distance
            timeCost = waitCost * max(instance['customer_%d' % customerID]['ready_time'] - arrivalTime, 0)
            # Update sub-route time cost
            subRouteTimeCost = subRouteTimeCost + timeCost
            # Update elapsed time
            elapsedTime = arrivalTime + instance['customer_%d' % customerID]['service_time']
            # Update last customer ID
            lastCustomerID = customerID
        # Calculate transport cost
        subRouteDistance = subRouteDistance + instance['distance_matrix'][lastCustomerID][0]
        subRouteTranCost = initCost + unitCost * subRouteDistance
        # Obtain sub-route cost
        subRouteCost = subRouteTimeCost + subRouteTranCost
        # Update total cost
        totalCost = totalCost + subRouteCost
    # print("finalizou certo - custo total = " + str(totalCost))
    return totalCost, len(route)


# def d(ind1, ind2):
    return ind1, ind2
    c1 = ind2route(ind1, instance)
    c2 = ind2route(ind2, instance)
    remove1 = random.randint(0,len(c1)-1)
    remove2 = random.randint(0,len(c2)-1)
    aux1 = c1[remove1] #The part that will be removed from c2
    aux2 = c2[remove2] #The part that will be removed from c1

    for i in c1[remove1]:
        c2.remove(i)
    for j in c2[remove2]:
        c1.remove(j)

    while 1:
        randonPosition = random.randint(0,len(aux1)-1)
        for i in range(0,len(c2)-1):
            c2[i].insert(aux1[randonPosition])
        if(len(aux1) == 0):
            break

    while 1:
        randonPosition = random.randint(0,len(aux2)-1)
        c1[randonC1Part].insert(aux2[randonPosition])
        if(len(aux2) == 0):
            break
    
    return c1.join('').split(''), c2.join('')


def retornaRandint(individual):
    individualSize = len(individual)
    aux1 = random.randint(1,individualSize-2)
    aux2 = random.randint(1,individualSize-2)
    return aux1, aux2

def consRouteInvMut(individual):
    aux1, aux2 = retornaRandint(individual)
    while(aux2 == aux1 or aux2-2 == aux1 or aux1-2==aux2):
        aux1, aux2 = retornaRandint(individual)
    
    individual1 = individual[0:min(aux1,aux2)]
    individual2 = individual[min(aux1,aux2):max(aux1,aux2)]
    individual3 = individual[max(aux1,aux2)::]

    individual2 = individual2[::-1]

    return individual1 + individual2 + individual3

def gaVRPTW(instName, unitCost, initCost, waitCost, indSize, popSize, cxPb, mutPb, NGen, exportCSV=False):
    txt = open('resultado.txt','w')
    jsonFile = instName + '.json'
    with open(jsonFile) as f:
        instance = load(f)
    creator.create('FitnessMax', base.Fitness, weights=(-1.0,-1.0))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    # Attribute generator
    toolbox.register('indexes', random.sample, range(1, indSize + 1), indSize)
    # Structure initializers
    toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indexes)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)
    # Operator registering
    toolbox.register('evaluate', evalVRPTW, instance=instance, unitCost=unitCost, initCost=initCost, waitCost=waitCost)
    toolbox.register('select', tools.selSPEA2)
    toolbox.register('mate', pmx)
    toolbox.register("selTournament", tools.selTournament, tournsize=2)
    toolbox.register('mutate', consRouteInvMut)
    pop = toolbox.population(n=popSize)
    archive = []
    print('Start of evolution')
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    print('  Evaluated %d individuals' % len(pop))
    # Begin the evolution
    for g in range(NGen):
        print('-- Generation %d --' % g)
        # Select the next generation individuals
        archive = toolbox.select(pop + archive , int(popSize/2)) #archive = toolbox.select(pop + archive , popSize/2)
        mating_pool = toolbox.selTournament(archive, k=popSize)
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, mating_pool))
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxPb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < mutPb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # Evaluate the individuals with an invalid fitness
        invalidInd = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalidInd)
        #print(fitnesses)
        for ind, fit in zip(invalidInd, fitnesses):
            ind.fitness.values = fit
        print('  Evaluated %d individuals' % len(invalidInd))
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
    indices = retiraRepetido(pop)
    print('-- End of (successful) evolution --')

    
    for i in indices:
            printRoute(txt,ind2route(pop[i], instance))
            txt.write('Custo total: ' +  str(pop[i].fitness.values[0]))
            txt.write('\n'+'-'*100 + '\n'*2)
    
    #txt.close()
    print('FIM')
        #print('Fitness: (%s,%s)' % (i.fitness.values[0],i.fitness.values[1]))
    # print('Best individual: %s' % bestInd)
    # print('Fitness: (%s,%s)' % (bestInd.fitness.values[0],bestInd.fitness.values[1]))
    # printRoute(ind2route(bestInd, instance))
    # print('Total cost: %s' % bestInd.fitness.values[0])
