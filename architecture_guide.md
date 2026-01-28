Hexagonal Architecture with SOLID Principles and TDD
Overview
This document outlines how to structure a software project using Hexagonal Architecture (Ports and Adapters), SOLID principles, and Test-Driven Development (TDD).
Architecture Diagram
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL WORLD                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   REST API   │  │   CLI Tool   │  │   Web UI     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │      PRIMARY/DRIVING ADAPTERS         │
         │   (Controllers, Presenters, CLI)      │
         └───────────────┬───────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │       PRIMARY/DRIVING PORTS           │
         │      (Input Port Interfaces)          │
         └───────────────┬───────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    DOMAIN CORE                             │
│                  (Business Logic)                          │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Entities   │  │  Use Cases   │  │   Services   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │      SECONDARY/DRIVEN PORTS           │
         │     (Output Port Interfaces)          │
         └───────────────┬───────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │     SECONDARY/DRIVEN ADAPTERS         │
         │  (Repositories, External Services)    │
         └───────────────┬───────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE                            │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Database   │  │  External    │  │   Message    │   │
│  │              │  │  APIs        │  │   Queue      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────┘
Layer Descriptions
1. Domain Core (Center)
Purpose: Contains all business logic and rules. This layer is framework-agnostic and has no dependencies on external libraries.
Components:

Entities: Core business objects with identity
Value Objects: Immutable objects defined by their attributes
Domain Services: Business logic that doesn't belong to a single entity
Use Cases: Application-specific business rules (orchestration)

Key Principles:

No dependencies on outer layers
Pure business logic
Framework-independent
Highly testable

2. Ports (Interfaces)
Primary/Driving Ports (Inbound)
Purpose: Define how the outside world can interact with your application.
Examples:
typescript// Input port for use case
interface CreateUserUseCase {
  execute(request: CreateUserRequest): Promise<CreateUserResponse>;
}

interface GetUserUseCase {
  execute(userId: string): Promise<User>;
}
Secondary/Driven Ports (Outbound)
Purpose: Define what your domain needs from the outside world.
Examples:
typescript// Repository port
interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
}

// External service port
interface EmailService {
  sendWelcomeEmail(email: string, name: string): Promise<void>;
}

// Event publisher port
interface EventPublisher {
  publish(event: DomainEvent): Promise<void>;
}
3. Adapters
Primary/Driving Adapters (Inbound)
Purpose: Translate external requests into calls to your domain through primary ports.
Examples:

REST API Controllers
GraphQL Resolvers
CLI Commands
Message Queue Consumers
Scheduled Jobs

typescript// REST Controller (Primary Adapter)
class UserController {
  constructor(private createUser: CreateUserUseCase) {}

  async createUser(req: Request, res: Response) {
    const request = this.mapToRequest(req.body);
    const response = await this.createUser.execute(request);
    res.json(this.mapToResponse(response));
  }
}
Secondary/Driven Adapters (Outbound)
Purpose: Implement the secondary ports to interact with external systems.
Examples:

Database Repositories
External API Clients
File System Access
Message Queue Publishers
Email Services

typescript// Database Repository (Secondary Adapter)
class PostgresUserRepository implements UserRepository {
  constructor(private db: DatabaseConnection) {}

  async save(user: User): Promise<void> {
    await this.db.query(
      'INSERT INTO users (id, email, name) VALUES ($1, $2, $3)',
      [user.id, user.email, user.name]
    );
  }

  async findById(id: string): Promise<User | null> {
    const result = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0] ? this.mapToDomain(result.rows[0]) : null;
  }
}
SOLID Principles in Hexagonal Architecture
Single Responsibility Principle (SRP)
Each class/module has one reason to change:

Use Cases handle one specific business operation
Repositories handle only data persistence
Controllers handle only HTTP concerns

Open/Closed Principle (OCP)
Open for extension, closed for modification:

Add new adapters without changing the domain
Add new use cases without modifying existing ones
Use interfaces (ports) to allow different implementations

Liskov Substitution Principle (LSP)
Any implementation of a port should be substitutable:

Any repository implementation should work the same way
Mock implementations can replace real ones in tests

Interface Segregation Principle (ISP)
Clients shouldn't depend on interfaces they don't use:

Create specific ports for specific needs
Split large interfaces into smaller, focused ones

typescript// Good: Segregated interfaces
interface UserReader {
  findById(id: string): Promise<User | null>;
}

interface UserWriter {
  save(user: User): Promise<void>;
}

// Instead of one large interface with all methods
Dependency Inversion Principle (DIP)
High-level modules shouldn't depend on low-level modules. Both should depend on abstractions:

Domain depends on ports (interfaces), not concrete implementations
Adapters depend on ports and implement them
Dependency injection at the composition root

Test-Driven Development (TDD) Approach
Testing Layers
1. Domain/Use Case Tests (Unit Tests)
Test business logic in isolation using test doubles for ports:
typescriptdescribe('CreateUserUseCase', () => {
  it('should create a user successfully', async () => {
    // Arrange
    const mockRepo: UserRepository = {
      save: jest.fn(),
      findByEmail: jest.fn().mockResolvedValue(null)
    };
    const mockEmailService: EmailService = {
      sendWelcomeEmail: jest.fn()
    };
    const useCase = new CreateUserUseCase(mockRepo, mockEmailService);

    // Act
    const result = await useCase.execute({
      email: 'test@example.com',
      name: 'Test User'
    });

    // Assert
    expect(result.success).toBe(true);
    expect(mockRepo.save).toHaveBeenCalledWith(
      expect.objectContaining({
        email: 'test@example.com',
        name: 'Test User'
      })
    );
    expect(mockEmailService.sendWelcomeEmail).toHaveBeenCalled();
  });
});
2. Adapter Tests (Integration Tests)
Test that adapters correctly implement ports:
typescriptdescribe('PostgresUserRepository', () => {
  let repository: UserRepository;
  let testDb: TestDatabase;

  beforeEach(async () => {
    testDb = await TestDatabase.create();
    repository = new PostgresUserRepository(testDb.connection);
  });

  it('should save and retrieve a user', async () => {
    const user = new User('1', 'test@example.com', 'Test User');
    
    await repository.save(user);
    const retrieved = await repository.findById('1');

    expect(retrieved).toEqual(user);
  });
});
3. End-to-End Tests
Test the entire flow through primary adapters:
typescriptdescribe('User API', () => {
  it('should create a user via REST API', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'test@example.com',
        name: 'Test User'
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });
});
TDD Workflow

Red: Write a failing test
Green: Write minimal code to make it pass
Refactor: Improve the code while keeping tests green

Project Structure Example
src/
├── domain/
│   ├── entities/
│   │   ├── User.ts
│   │   └── Order.ts
│   ├── value-objects/
│   │   ├── Email.ts
│   │   └── Money.ts
│   ├── services/
│   │   └── PricingService.ts
│   └── events/
│       └── UserCreatedEvent.ts
│
├── application/
│   ├── use-cases/
│   │   ├── CreateUserUseCase.ts
│   │   ├── GetUserUseCase.ts
│   │   └── PlaceOrderUseCase.ts
│   └── ports/
│       ├── input/
│       │   ├── CreateUserUseCase.interface.ts
│       │   └── PlaceOrderUseCase.interface.ts
│       └── output/
│           ├── UserRepository.interface.ts
│           ├── OrderRepository.interface.ts
│           ├── EmailService.interface.ts
│           └── PaymentGateway.interface.ts
│
├── adapters/
│   ├── primary/
│   │   ├── rest/
│   │   │   ├── UserController.ts
│   │   │   └── OrderController.ts
│   │   ├── graphql/
│   │   │   └── UserResolver.ts
│   │   └── cli/
│   │       └── ImportUsersCommand.ts
│   │
│   └── secondary/
│       ├── persistence/
│       │   ├── PostgresUserRepository.ts
│       │   └── MongoOrderRepository.ts
│       ├── messaging/
│       │   └── RabbitMQEventPublisher.ts
│       └── external/
│           ├── StripePaymentGateway.ts
│           └── SendGridEmailService.ts
│
├── infrastructure/
│   ├── database/
│   │   └── DatabaseConnection.ts
│   ├── config/
│   │   └── Configuration.ts
│   └── di/
│       └── Container.ts (Dependency Injection)
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
Key Benefits
1. Testability

Domain logic is easily testable with no external dependencies
Adapters can be tested in isolation
Use test doubles for all external dependencies

2. Flexibility

Change databases without affecting business logic
Switch from REST to GraphQL by adding a new adapter
Replace external services easily

3. Maintainability

Clear separation of concerns
Business logic is protected from framework changes
Easy to understand and navigate

4. Technology Independence

Domain doesn't depend on frameworks
Can delay infrastructure decisions
Easy to upgrade or replace technologies

Implementation Checklist

 Define your domain entities and value objects
 Write use cases for your business operations
 Define port interfaces (both input and output)
 Implement use cases using TDD
 Create adapters for external systems
 Wire everything together with dependency injection
 Write integration tests for adapters
 Write end-to-end tests for critical flows

Common Pitfalls to Avoid

Leaking domain logic into adapters: Keep business rules in the domain
Anemic domain model: Entities should have behavior, not just data
Over-engineering: Start simple, add complexity only when needed
Wrong dependencies: Never let domain depend on adapters
Too many layers: Don't add layers just for the sake of it

Resources for Further Learning

Books:

"Implementing Domain-Driven Design" by Vaughn Vernon
"Clean Architecture" by Robert C. Martin
"Growing Object-Oriented Software, Guided by Tests" by Steve Freeman


Concepts:

Domain-Driven Design (DDD)
CQRS (Command Query Responsibility Segregation)
Event Sourcing




Remember: The goal is to create maintainable, testable software. Use these patterns as guidelines, not strict rules. Adapt them to your project's needs.