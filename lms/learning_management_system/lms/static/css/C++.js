document.addEventListener('DOMContentLoaded', () => {
    const topics = [
        { 
            title: "Module 1: C++ Fundamentals & OOP", 
            items: [
                "C to C++ Transition (iostream, namespaces)", 
                "Variables, Types, and Control Flow",
                "Functions, Overloading, and Default Arguments",
                "Pointers, References, and Memory Management (new/delete)",
                "Classes, Objects, Constructors, and Destructors"
            ] 
        },
        { 
            title: "Module 2: Advanced OOP & Polymorphism", 
            items: [
                "Inheritance (Single, Multiple, Virtual Base)", 
                "Polymorphism: Virtual Functions & Abstract Classes",
                "Operator Overloading & Custom Types",
                "Exception Handling (try-catch-throw)",
                "RAII (Resource Acquisition Is Initialization) Pattern"
            ] 
        },
        { 
            title: "Module 3: Standard Template Library (STL)", 
            items: [
                "Containers: Vector, List, Deque, Map, Set", 
                "Iterators: The STL's Pointer Abstraction",
                "Algorithms: Sort, Search, Transform, Lambda Expressions",
                "Smart Pointers (unique_ptr, shared_ptr, weak_ptr)",
                "String Handling and Streams (File I/O)"
            ] 
        },
        { 
            title: "Module 4: Modern C++ (C++11/17/20/23)", 
            items: [
                "Move Semantics (rvalue references, move constructor)", 
                "Concurrency and Multithreading (std::thread)",
                "Type Deduction (auto, decltype)",
                "Modules & Build Systems (CMake/Bazel)",
                "Templates, Concepts, and Generic Programming"
            ] 
        }
    ];

    const topicsContainer = document.querySelector('.topics-container');

    topics.forEach(module => {
        const card = document.createElement('div');
        card.className = 'topic-card';

        const title = document.createElement('h3');
        title.textContent = module.title;

        const ul = document.createElement('ul');
        module.items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });

        card.appendChild(title);
        card.appendChild(ul);
        topicsContainer.appendChild(card);
    });

    // Optional: Add smooth scrolling for the "EXPLORE COURSE" button
    document.querySelector('.btn-primary').addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});