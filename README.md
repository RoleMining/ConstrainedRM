# Constrained Role Mining
<p align="justify">
Role Based Access Control (RBAC)   has become a de-facto standard to control the access to restricted resources in complex  systems and is widely deployed in many commercially available applications, including operating systems, databases and other software. 
The migration process towards RBAC, starting from the current access configuration,
relies on the design of role mining techniques whose aim is to define suitable roles that implement the given access policies. 
To transform the roles automatically output by the mining procedures and  to effectively capture the status of the organization under analysis, a number 
of constraints can be used. Such constraints can limit some characteristics such as the number of roles assigned to an user, the number of persmission assigned to a role or the number of permission included in a role 
on the resulting roles and  produce a resulting role set that is effectively usable in real world situations.
</p>

<p align="justify">
The Python code available in the folders PRUCC implements two heuristics that satisfy at the same time constraints imposed both on the number of permissions included in a role and on  the number of roles a particular user can have. 
<ul>
  <li>The first heuristic executes a pre-processing phase where roles are firstly assigned according to the permission cardinality constraint, and then the remaining permissions are accommodated. 
  <li>The second heuristic combines production of new roles and  filtering of not compliant roles during the mining phase.
</ul>
The Python code available in the folders PostProcessing implements two heuristics (the heuristics are developed in the post-processing framework which means that the heuristic requires as input a precomputed role mining assignment):
<ul>
  <li> The first heuristic ensures that each user has assigned no more than a fixed number of roles.
  <li>The second heuristic ensures that each role has assigned no more than a fixed number of permissions.
</ul>
</p>
 
<p align="justify"> 
More details about the first two heuristics can be found in the paper: Role Mining Heuristics for Permission-Role-Usage Cardinality Constraints,  Carlo Blundo, Stelvio Cimato, Luisa Siniscalchi, The Computer Journal, 2021; https://doi.org/10.1093/comjnl/bxaa186
</p>

