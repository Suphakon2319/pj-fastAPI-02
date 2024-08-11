from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
import itertools
import operator
import re
from itertools import permutations

app = FastAPI()

# สำหรับ API คำนวณ
class Problem(BaseModel):
    Problem: str

def parse_expression(expression: str):
    expression = expression.replace(" ", "")
    numbers = list(map(float, re.findall(r'-?\d+\.?\d*', expression)))
    operators = re.findall(r'[+\-*/]', expression)
    return numbers, operators

@app.post("/calculate/")
async def calculate_expression(problem: Problem):
    expression = problem.Problem
    numbers, operators = parse_expression(expression)
    
    if len(numbers) == 0:
        return {"error": "No numbers provided"}
    
    if len(numbers) > 5:
        numbers = numbers[:5]
        operators = operators[:4]
    
    try:
        result = eval(expression)
    except ZeroDivisionError:
        return {"error": "Division by zero is not allowed"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    
    response = {
        "numbers": numbers,
        "operators": operators,
        "result": result,
    }

    if result > 24:
        response["comparison"] = "greater than 24"
    elif result < 24:
        response["comparison"] = "less than 24"
    else:
        response["comparison"] = "equal to 24"
    
    return response

# สำหรับ API สร้างตัวเลข
def check_24(numbers: List[int]) -> bool:
    ops = [operator.add, operator.sub, operator.mul, operator.truediv]
    
    for number_permutation in itertools.permutations(numbers):
        for ops_combination in itertools.product(ops, repeat=3):
            try:
                result1 = ops_combination[0](number_permutation[0], number_permutation[1])
                result2 = ops_combination[1](result1, number_permutation[2])
                result3 = ops_combination[2](result2, number_permutation[3])

                if abs(result3 - 24) < 1e-6:
                    return True
                
                result1 = ops_combination[0](number_permutation[0], ops_combination[1](number_permutation[1], number_permutation[2]))
                result2 = ops_combination[2](result1, number_permutation[3])
                
                if abs(result2 - 24) < 1e-6:
                    return True

            except ZeroDivisionError:
                continue
    return False

@app.get("/generate_numbers")
async def generate_numbers():
    max_attempts = 1000
    for _ in range(max_attempts):
        numbers = [random.randint(1, 9) for _ in range(4)]
        if check_24(numbers):
            return {
                "a": str(numbers[0]),
                "b": str(numbers[1]),
                "c": str(numbers[2]),
                "d": str(numbers[3])
            }
    raise HTTPException(status_code=404, detail="No valid set of numbers found after many attempts.")

# สำหรับ API คำนวณตัวเลข
class CalculationRequest(BaseModel):
    a: str
    b: str
    c: str
    d: str

class CalculationRequest(BaseModel):
    a: str
    b: str
    c: str
    d: str

def calculate_expression(nums, ops):
    try:
        expr = f"({nums[0]} {ops[0]} {nums[1]}) {ops[1]} ({nums[2]} {ops[2]} {nums[3]})"
        return eval(expr), expr
    except ZeroDivisionError:
        return float('inf'), expr

@app.post("/compute")
async def compute(data: CalculationRequest):
    try:
        # Convert string values to float
        a = float(data.a)
        b = float(data.b)
        c = float(data.c)
        d = float(data.d)
        
        nums = [a, b, c, d]
        ops = ['+', '-', '*', '/']
        
        closest_result = float('inf')
        closest_expr = ""
        
        # Check all permutations of numbers and operators
        for num_perm in permutations(nums):
            for op_perm in permutations(ops, 3):
                result, expr = calculate_expression(num_perm, op_perm)
                if abs(result - 24) < abs(closest_result - 24):
                    closest_result = result
                    closest_expr = expr

        steps = [
            f"Best result: {closest_expr}",
            f"= {closest_result}"
        ]

        return {"steps": steps, "result": closest_result}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input value")