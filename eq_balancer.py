import re
from sympy import Matrix, lcm


def balance(reac, prod):
    elementList = []
    elementMatrix = []
    reactants = reac.replace(' ', '').split("+")
    products = prod.replace(' ', '').split("+")

    def add_to_matrix(element, index, count, side):
        if index == len(elementMatrix):
            elementMatrix.append([])
            for _ in elementList:
                elementMatrix[index].append(0)
        if element not in elementList:
            elementList.append(element)
            for i in range(len(elementMatrix)):
                elementMatrix[i].append(0)
        column = elementList.index(element)
        elementMatrix[index][column] += count * side

    def find_elements(segment, index, multiplier, side):
        elements_and_numbers = re.split('([A-Z][a-z]?)', segment)
        i = 0
        while i < len(elements_and_numbers) - 1:  # last element always blank
            i += 1
            if len(elements_and_numbers[i]) > 0:
                if elements_and_numbers[i + 1].isdigit():
                    count = int(elements_and_numbers[i + 1]) * multiplier
                    add_to_matrix(elements_and_numbers[i], index, count, side)
                    i += 1
                else:
                    add_to_matrix(elements_and_numbers[i], index, multiplier, side)

    def compound_decipher(compound, index, side):
        segments = re.split('(\([A-Za-z0-9]*\)[0-9]*)', compound)
        for segment in segments:
            if segment.startswith("("):
                segment = re.split('\)([0-9]*)', segment)
                multiplier = int(segment[1])
                segment = segment[0][1:]
            else:
                multiplier = 1
            find_elements(segment, index, multiplier, side)

    for i in range(len(reactants)):
        compound_decipher(reactants[i], i, 1)
    for i in range(len(products)):
        compound_decipher(products[i], i + len(reactants), -1)
    elementMatrix = Matrix(elementMatrix)
    elementMatrix = elementMatrix.transpose()
    solution = elementMatrix.nullspace()[0]
    multiple = lcm([val.q for val in solution])
    solution = multiple * solution
    coEffi = solution.tolist()
    output = ""
    for i in range(len(reactants)):
        output += f"**{coEffi[i][0]}**" + reactants[i]
        if i < len(reactants) - 1:
            output += " + "
    output += " → "
    for i in range(len(products)):
        output += f"**{coEffi[i + len(reactants)][0]}**" + products[i]
        if i < len(products) - 1:
            output += " + "
    return output
