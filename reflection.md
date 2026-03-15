# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design will consist of several classes: Owner, Pet, Task, Schedule. 
Each owner will have pets they are assigned to, and each pet will have pet care
tasks that can be tracked. Schedule will be a separate class that will contain
a list of Task objects for each pet.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design changed slightly during implementation. Copilot was suggesting a fix
for the built-in datetime class for Python, which is a bit naive and doesn't
account for varying timezones, which can break logic for something that relies 
on correct time as much as a scheduler. It also improved my UML diagram by 
adding a few missing attributes such as a list of Pets for each Owner. I made
this change because Owners should be able to own multiple Pets and thus have
specific tasks for each particular pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considered constraints like time zones and priority. I decided
these constraints mattered the most because in an actual app if it was deployed,
you'd need to consider the user experience and thus time zones and priority
would become important. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler makes a tradeoff by using straightforward rules instead of a more 
complex optimization model with many constraints. This means the system is 
easier to understand, faster to run, and simpler to debug, but it may not always 
generate the absolute “best” schedule in every edge case. This tradeoff is 
reasonable for this scenario because PawPal is a starter app, and reliability, 
readability, and maintainability matter more than optimization.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI mostly for brainstorming class design, validating relationships in my 
UML, and implementing method stubs into working code. It was also helpful for 
improving edge-case handling, like timezone-aware datetime validation and 
conflict checks. The most useful prompts were specific implementation asks, like 
“implement this class method” or “review this logic for missing relationships.”

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One time I did not accept AI output as-is was around conflict detection 
behavior. The suggested logic treated conflicts globally across all pets, but I 
had to think about whether conflict scope should be per pet or per owner. I 
verified behavior by writing tests and checking the failing scenario, then used 
that result to identify the design decision clearly.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task creation validation (timezone-aware datetimes, duration checks), 
schedule operations (add/remove/get), sorting and filtering behavior, and 
overlap conflict detection. I also tested that list-return methods do not expose 
internal mutable state. These were important because they target both core 
functionality and common edge cases.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am moderately confident that the scheduler works correctly for the current 
project scope. Most tests pass, and the remaining failure highlights a design 
choice rather than a crash-level bug. If I had more time, I would test recurring 
task expansion in date ranges, cross-timezone user input, and higher task 
performance.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the system structure and how well the classes map to 
real app behavior. The separation between owner/pet/task data and scheduler 
logic made the code easier to reason about.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would redesign recurrence handling to generate future 
instances more explicitly and make conflict scope configurable. I would also add 
stronger UI controls for editing/completing tasks directly.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

A key takeaway for me was that AI is most useful when I give precise prompts and 
then verify outputs with tests. It sped up implementation, but design decisions 
and correctness still depended on my own judgment.