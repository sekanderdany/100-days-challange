student_score = [78, 65, 89, 86, 55, 91, 64, 89, 96, 92, 88, 75, 99, 73, 84, 91, 87, 77, 94, 81, 79, 100, 67, 92, 87, 94, 82, 76, 88, 95, 89]

total_exam_score = sum(student_score)
print(f"Total Exam Score: {total_exam_score}")

sum = 0
for score in student_score:
    sum += score

print(f"Total Exam Score using loop: {sum}")

highest_score = max(student_score)
print(f"The highest score in the class is using max: {highest_score}")

highest_score_with_loop = 0
for score in student_score:
    if score > highest_score_with_loop:
        highest_score_with_loop = score

print(f"The highest score in the class is using loop: {highest_score_with_loop}")