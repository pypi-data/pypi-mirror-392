insert_element = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, pos, value;

    cout << "Size of Array: ";
    cin >> size;

    cout << "Enter the elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the element to insert: ";
    cin >> value;
    cout << "Enter the position to insert: ";
    cin >> pos;

    if (pos<0 || pos>size){
        cout << "Invalid position!" << endl;
    }
    else {
        for (int i = size; i > pos; i--){
            arr[i] = arr[i - 1];
        }

        arr[pos] = value;
        size++;
        cout << "Array after insertion: " << endl;
        for (int i = 0; i < size; i++) {
            cout << arr[i] << " ";
        }
    }

    return 0;
}
"""

delete_element = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, pos;

    cout << "Size of Array: ";
    cin >> size;

    cout << "Enter the elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the position: ";
    cin >> pos;

    if (pos <0 || pos >=size) {
        cout << "Invalid position!" << endl;
    } else {
        for (int i = pos; i < size - 1; i++) {
            arr[i] = arr[i + 1];
        }

        size--;
        cout << "Array after deletion: " << endl;
        for (int i = 0; i < size; i++) {
            cout << arr[i] << " ";
        }
        cout << endl;
    }
    return 0;
}
"""
linear_search = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, value;
    int loc = -1; 

    cout << "Enter the size of array: ";
    cin >> size;

    cout << "Enter elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the element to find: ";
    cin >> value;

    for (int i = 0; i < size; i++) {
        if (arr[i] == value) {
            loc = i; 
            break;   
        }
    }

    if (loc != -1) {
        cout << "Element " << value << " found at position: " << loc << endl;
    } else {
        cout << "Element " << value << " not found." << endl;
    }

    return 0;
}
"""

bubble_sort_asc = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    for (int i = 0; i < size - 1; i++){
        for (int j = 0; j < size - i - 1; j++) {
            if (arr[j] > arr[j + 1]) { // use < for descending order
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""

selection_sort = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    // Selection Sort Algorithm
    for (int i = 0; i < size - 1; i++) {
        
        int min_idx = i;
        for (int j = i + 1; j < size; j++) {
            if (arr[j] < arr[min_idx]){ // use > for descending order
                min_idx = j;
            }
        }

        int temp = arr[min_idx];
        arr[min_idx] = arr[i];
        arr[i] = temp;
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""
stack = """
#include <iostream>
using namespace std;

#define STACK_SIZE 100

int stack[STACK_SIZE];
int top = -1; 

void push(int value) {
    if (top >= STACK_SIZE - 1) {
        cout << "Overflow!" << endl;
    } else {
        top++; 
        stack[top] = value; 
        cout << value << " pushed in stack" << endl;
    }
}

void pop() {
    if (top == -1) {
        cout << "Underflow!" << endl;
    } else {
        int poppedValue = stack[top]; 
        top--; 
        cout << poppedValue << " popped from stack." << endl;
    }
}

void display() {
    if (top == -1) {
        cout << "Empty." << endl;
    } else {
        cout << "Elements in stack:" << endl;
        for (int i = top; i >= 0; i--) {
            cout << stack[i] << endl;
        }
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Push (Add)" << endl;
        cout << "2. Pop (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to push: ";
                cin >> value;
                push(value);
                break;
            case 2:
                pop();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice" << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

insertion_sort = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    // Insertion Sort Algorithm
    for (int i = 1; i < size; i++) {

        int key = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > key) { // invert signs for descending order
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""

linear_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 100
int queue[QUEUE_SIZE];
int front = -1;
int rear = -1;

void enqueue(int value) {
    if (rear >= QUEUE_SIZE - 1) {
        cout << "Overflow!" << endl;
    } else {
        if (front == -1) {
            front = 0;
        }
        rear++;
        queue[rear] = value;
        cout << value << " enqueued to the queue." << endl;
    }
}

void dequeue() {
    if (front == -1 || front > rear) {

        cout << "Queue Underflow!." << endl;
    } else {
        int dequeuedValue = queue[front];
        front++;
        cout << "Dequeued " << dequeuedValue << " from the queue." << endl;
        
        if (front > rear) {
            front = -1;
            rear = -1;
        }
    }
}

void display() {
    if (front == -1 || front > rear) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue:" << endl;
        for (int i = front; i <= rear; i++) {
            cout << queue[i] << " ";
        }
        cout << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Add" << endl;
        cout << "2. Remove" << endl;
        cout << "3. Display" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

circular_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 5 

int queue[QUEUE_SIZE];
int front = -1; 
int rear = -1;  

bool isFull() {
    return (front == (rear + 1) % QUEUE_SIZE);
}

bool isEmpty() {
    return (front == -1);
}

void enqueue(int value) {
    if (isFull()) {
        cout << "Queue Overflow" << endl;
    } else {
        if (isEmpty()) {
            front = 0;
        }
        rear = (rear + 1) % QUEUE_SIZE;
        queue[rear] = value; 
        cout << value << " enqueued to the queue." << endl;
    }
}

void dequeue() {
    if (isEmpty()) {
        cout << "Queue Underflow!" << endl;
    } else {
        int dequeuedValue = queue[front];
        
        if (front == rear) {
            front = -1;
            rear = -1;
        } else {
            front = (front + 1) % QUEUE_SIZE;
        }
        
        cout << "Dequeued " << dequeuedValue << " from the queue." << endl;
    }
}

void display() {
    if (isEmpty()) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue:" << endl;
        cout << "FRONT -> ";
        
        int i = front;
        while (true) {
            cout << queue[i] << " ";
            if (i == rear) {
                break; 
            }
            i = (i + 1) % QUEUE_SIZE;
        }
        
        cout << "<- REAR" << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Enqueue (Add)" << endl;
        cout << "2. Dequeue (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""
prioriy_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 100

int queue[QUEUE_SIZE];
int front = -1; 
int rear = -1;  

bool isFull() {
    return (rear >= QUEUE_SIZE - 1);
}

bool isEmpty() {
    return (front == -1 || front > rear);
}

void enqueue(int value) {
    if (isFull()) {
        cout << "Queue Overflow!" << endl;
        return;
    }

    if (isEmpty()) {
        front = 0;
        rear = 0;
        queue[0] = value;
    } else {
        int j = rear;
        
        while (j >= front && queue[j] < value) {
            queue[j + 1] = queue[j];
            j--;
        }
        
        queue[j + 1] = value;
        rear++; 
    }
    cout << value << " enqueued to the priority queue." << endl;
}

void dequeue() {
    if (isEmpty()) {
        cout << "Queue Underflow!" << endl;
    } else {
        int dequeuedValue = queue[front];
        
        if (front == rear) {
            front = -1;
            rear = -1;
        } else {
            front++;
        }
        
        cout << "Dequeued " << dequeuedValue << "(highest priority) from the queue." << endl;
    }
}

void display() {
    if (isEmpty()) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue(from highest):" << endl;
        cout << "FRONT -> ";
        for (int i = front; i <= rear; i++) {
            cout << queue[i] << " ";
        }
        cout << "<- REAR" << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Enqueue (Add)" << endl;
        cout << "2. Dequeue (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

linked_list = """
#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
};

Node* head = NULL;

void display() {
    if (head == NULL) {
        cout << "The list is empty." << endl;
        return;
    }
    Node* temp = head;
    cout << "List (Head to Tail): HEAD -> ";
    while (temp != NULL) {
        cout << temp->data << " -> ";
        temp = temp->next;
    }
    cout << "NULL" << endl;
}

void insertAtBeginning(int data) {
    Node* newNode = new Node();
    newNode->data = data;
    newNode->next = head;
    head = newNode;
    cout << data << " inserted at the beginning." << endl;
    display();
}

void insertAtEnd(int data) {
    Node* newNode = new Node();
    newNode->data = data;
    newNode->next = NULL; 

    if (head == NULL) {
        head = newNode;
    } else {
        Node* temp = head;
        while (temp->next != NULL) {
            temp = temp->next;
        }
        temp->next = newNode;
    }
    
    cout << data << " inserted at the end." << endl;
    display();
}

void insertAtPosition(int data, int pos) {
    if (pos < 1) {
        cout << "Invalid position. Position must be 1 or greater." << endl;
        return;
    }

    if (pos == 1) {
        insertAtBeginning(data);
        return;
    }

    Node* newNode = new Node();
    newNode->data = data;

    Node* prev = head;
    for (int i = 1; i < pos - 1; i++) {
        if (prev == NULL) {
            cout << "Position " << pos << " is out of bounds." << endl;
            delete newNode; 
            return;
        }
        prev = prev->next;
    }
    if (prev == NULL) {
        cout << "Position " << pos << " is out of bounds." << endl;
        delete newNode;
        return;
    }

    newNode->next = prev->next;
    prev->next = newNode;

    cout << data << " inserted at position " << pos << "." << endl;
    display();
}

void deleteFromBeginning() {
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }
    Node* temp = head;
    head = head->next;
    int deletedValue = temp->data;
    delete temp;

    cout << deletedValue << " deleted from the beginning." << endl;
    display();
}

void deleteFromEnd() {
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }

    Node* temp = head;
    Node* secondLast = NULL;

    if (temp->next == NULL){
        int deletedValue = temp->data;
        delete head;
        head = NULL;
        cout << deletedValue << " deleted from the end." << endl;
        display();
        return;
    }

    while (temp->next != NULL) {
        secondLast = temp;
        temp = temp->next;
    }
    int deletedValue = temp->data;
    secondLast->next = NULL;
    
    delete temp;
    cout << deletedValue << " deleted from the end." << endl;
    display();
}

void deleteFromPosition(int pos) {
    if (pos < 1) {
        cout << "Invalid position. Position must be 1 or greater." << endl;
        return;
    }
    
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }

    if (pos == 1) {
        deleteFromBeginning();
        return;
    }

    Node* prev = head;
    for (int i = 1; i < pos - 1; i++) {
        if (prev == NULL || prev->next == NULL) {
            cout << "Position " << pos << " is out of bounds." << endl;
            return;
        }
        prev = prev->next;
    }

    if (prev == NULL || prev->next == NULL) {
        cout << "Position " << pos << " is out of bounds." << endl;
        return;
    }

    Node* temp = prev->next;
    prev->next = temp->next;
    
    int deletedValue = temp->data;
    delete temp;
    cout << deletedValue << " deleted from position " << pos << "." << endl;
    display();
}


int main() {
    int choice, value, position;

    do {
        cout << "1. Display List" << endl;
        cout << "2. Insert at Beginning" << endl;
        cout << "3. Insert at End" << endl;
        cout << "4. Insert at Specific Position" << endl;
        cout << "5. Delete from Beginning" << endl;
        cout << "6. Delete from End" << endl;
        cout << "7. Delete from Specific Position" << endl;
        cout << "8. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                display();
                break;
            case 2:
                cout << "Enter value to insert: ";
                cin >> value;
                insertAtBeginning(value);
                break;
            case 3:
                cout << "Enter value to insert: ";
                cin >> value;
                insertAtEnd(value);
                break;
            case 4:
                cout << "Enter value to insert: ";
                cin >> value;
                cout << "Enter position (1-based): ";
                cin >> position;
                insertAtPosition(value, position);
                break;
            case 5:
                deleteFromBeginning();
                break;
            case 6:
                deleteFromEnd();
                break;
            case 7:
                cout << "Enter position to delete (1-based): ";
                cin >> position;
                deleteFromPosition(position);
                break;
            case 8:
                cout << "Exiting program. Goodbye!" << endl;
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 8);

    Node* temp = head;
    while (temp != NULL) {
        Node* toDelete = temp;
        temp = temp->next;
        delete toDelete;
    }
    return 0;
}
"""
answer_dict = {
    "insertelement": insert_element,
    "deleteelement": delete_element,
    "linearsearch": linear_search,
    "bubblesort": bubble_sort_asc,
    "selectionsort": selection_sort,
    "stack": stack,
    "insertionsort": insertion_sort,
    "linearqueue": linear_queue,
    "circularqueue": circular_queue,
    "priorityqueue": prioriy_queue,
    "linkedlist": linked_list,
}