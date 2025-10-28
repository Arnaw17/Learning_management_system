document.addEventListener('DOMContentLoaded', () => {
    const topics = [
        { 
            title: "Module 1: Core Java and OOP", 
            items: [
                "JDK, JRE, and JVM Architecture", 
                "Variables, Data Types, and Operators",
                "Control Flow (if/else, switch, loops)",
                "Classes, Objects, Constructors, and 'this' keyword",
                "Encapsulation, Inheritance, and Polymorphism"
            ] 
        },
        { 
            title: "Module 2: Advanced Language Features", 
            items: [
                "Arrays, Strings, and the Utility Classes", 
                "Collections Framework (List, Set, Map, Queue)",
                "Exception Handling (try-catch-finally)",
                "Multithreading and Concurrency",
                "Input/Output (I/O) Streams and File Handling"
            ] 
        },
        { 
            title: "Module 3: Database & Web Fundamentals", 
            items: [
                "JDBC (Java Database Connectivity)", 
                "Connecting Java to MySQL/PostgreSQL",
                "Introduction to Servlets and JSPs",
                "Maven/Gradle Build Tools",
                "Version Control with Git"
            ] 
        },
        { 
            title: "Module 4: Enterprise Development (Spring)", 
            items: [
                "Introduction to **Spring Boot** and Microservices", 
                "Dependency Injection (DI) and IOC Container",
                "Building RESTful Web Services (APIs)",
                "Data Persistence with Spring Data JPA",
                "Security Basics with Spring Security"
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