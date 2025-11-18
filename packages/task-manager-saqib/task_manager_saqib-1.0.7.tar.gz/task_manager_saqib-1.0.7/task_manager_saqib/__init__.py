

tasks = []

def Add():
    task = input("---Enter a task---: ")
    tasks.append(task)
    print("Task added successfully!")
    print(task)

def Remove():
    task = input("---Enter a task to remove---: ")
    if task in tasks:
        tasks.remove(task)
        print("---Task removed successfully!---")
    else:
        print("---Task not found---")

def Update():
    task = input("---Enter a task to Update---: ")
    if task in tasks:
        tasks.remove(task)
        task = input("Enter Task again to update: ")
        tasks.append(task)
        print("Task updated successfully")


def run_task_manager():
    print("---Task Manager---")

    while True:
        print("\n1:-- Enter into Task Manager--")
        print("2:-- Exit --")
        option = int(input("Enter any option: "))

        if option == 2:
            print("---Successfully Exited---")
            break

        elif option == 1:
            while True:
                print("\n1: --Add Task--")
                print("2: --Remove Task--")
                print("3: --Update Task--")
                print("4: --View tasks--")
                print("5: Exit")

                choice = int(input("Enter a Choice: "))

                if choice == 5:
                    print("--Exited Task Manager--")
                    break
                elif choice == 1:
                    Add()
                elif choice == 2:
                    Remove()
                elif choice == 3:
                    Update()
                elif choice == 4:
                    print(f"Tasks are {tasks}\n")
                else:
                    print("%%Invalid choice%%.")
