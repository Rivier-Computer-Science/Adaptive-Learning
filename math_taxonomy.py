topic_colors = { # Green to Red
    "Arithmetic": "97,130,100", 
    "Algebra": "97,130,100",    
    "Geometry": "121,172,120",
    "Trigonometry": "176,217,177",
    "Statistics_and_Probability": "228,247,143",
    "Pre-Calculus": "253,255,188",
    "Calculus": "255,238,187",
    "Advanced_Calculus": "255,220,184",
    "Discrete_Mathematics": "255,193,182",
    "Linear_Algebra": "250,135,127",
    "Advanced_Statistics": "239,75,75",
    "Mathematical_Proofs_and_Theory": "189,87,78"
}

topics_and_subtopics = {
    "Arithmetic": [
        "Recognizing Shapes",
        "Number Sense",
        "Basic Operations",
        "Number Properties",
        "Laws",
        "Place Values",
        "Time and Calendar",
        "Money",
        "Estimation and Rounding",
        "Negative Numbers",
        "Absolute Value",
        "Fractions",
        "Decimals",
        "Factors and Multiples",
        "Exponents and Square Roots",
        "Percentages",
        "Ratios and Proportions",
        "Measurements and Units",
        "Graphs",
        "Patterns and Sequences"
    ],
    "Algebra": [
        "Algebraic Expressions",
        "Linear Equations",
        "Inequalities",
        "Polynomials",
        "Systems of Equations",
        "Functions",
        "Quadratic Equations"
    ],
    "Geometry": [
        "Basic Geometric Shapes",
        "Congruence and Similarity",
        "Pythagorean Theorem",
        "Circles",
        "Area and Volume",
        "Coordinate Geometry",
        "Trigonometry"
    ],
    "Trigonometry": [
        "Trigonometric Ratios",
        "Graphs of Trigonometric Functions",
        "Trigonometric Identities",
        "Applications"
    ],
    "Statistics and Probability": [
        "Descriptive Statistics",
        "Probability Basics",
        "Combinations and Permutations",
        "Random Variables and Distributions",
        "Inferential Statistics"
    ],
    "Pre-Calculus": [
        "Advanced Algebra",
        "Complex Numbers",
        "Exponential and Logarithmic Functions",
        "Advanced Trigonometry",
        "Sequences and Series",
        "Matrices"
    ],
    "Calculus": [
        "Limits",
        "Derivatives",
        "Integration",
    ],
    "Advanced Calculus": [
        "Series and Sequences",
        "Vector Calculus",
        "Multivariable Calculus",
        "Differential Equations",
        "Special Topics"
    ],
    "Discrete Mathematics": [
        "Logic and Proofs",
        "Set Theory",
        "Combinatorics",
        "Graph Theory",
        "Algorithms and Complexity"
    ],
    "Linear Algebra": [
        "Vector Spaces",
        "Linear Transformations",
        "Advanced Matrices",
        "Systems of Linear Equations",
        "Advanced Topics"
    ],
    "Advanced Statistics": [
        "Regression Analysis",
        "ANOVA",
        "Nonparametric Tests",
        "Time Series Analysis",
        "Bayesian Statistics"
    ],
    "Mathematical Proofs and Theory": [
        "Introduction to Proofs",
        "Number Theory",
        "Group Theory",
        "Real Analysis",
        "Topology"
    ]
}



subsub_topics = {
    # Arithmetic
    "Recognizing Shapes": ["Basic Shapes","Symmetry"],
    "Number Sense": ["Counting","Comparisons"],
    "Basic Operations": ["Addition", "Subtraction", "Multiplication", "Division","Zero", "Operations Order"],
    "Number Properties": ["Odd and Even","Prime"],
    "Laws": ["Associative","Commutative","Distributive"],
    "Place Values": ["Units", "Writing Large Numbers"],
    "Time and Calendar": ["Reading Clocks", "Measuring Time", "Calendar Skills"],
    "Money": ["Coins and Bills","Basic Transactions","Budgeting"],
    "Estimation and Rounding": ["Nearest decimal", "Estimate Operations"],
    "Negative Numbers": ["Concept", "Number Line","Basic Operations","Temperatures", "Debt"],
    "Absolute Value": ["Number Line", "Distance from Zero"],
    "Fractions": ["Understanding", "Simplifying", "Operations"],
    "Decimals": ["Conversion", "Operations"],
    "Factors and Multiples": ["Finding Factors", "Common Multiples", "GCF", "LCM"],
    "Exponents and Square Roots": ["Exponentiation as Repeated Multiplication", "Square Roots"],
    "Percentages": ["Calculating percentages", "Percentage increase/decrease", "Real-world applications"],
    "Ratios and Proportions": ["Understanding ratios", "Solving proportion problems", "Direct and inverse variation"],
    "Measurements and Units": ["Standard Units", "Metric Units", "Converting Units"],
    "Graphs": ["Pictograph", "Line graph"],
    "Patterns and Sequences": ["Arithmetic Sequences"],
    # Algebra
    "Algebraic Expressions": ["Simplifying", "Evaluating expressions", "Combining like terms"],
    "Linear Equations": ["Solving one-variable", "Multi-variable equations", "Word problems"],
    "Inequalities": ["Solving", "Graphing on a number line", "Compound inequalities"],
    "Polynomials": ["Adding", "Subtracting", "Multiplying", "Dividing", "Polynomial long division"],
    "Systems of Equations": ["Methods of solving", "Applications"],
    "Functions": ["Notation", "Domain and Range", "Inverse Functions"],
    "Quadratic Equations": ["Factoring", "Quadratic formula", "Completing the square", "Graphing parabolas"],
    # Geometry
    "Basic Geometric Shapes": ["Properties of triangles", "Quadrilaterals", "Polygons"],
    "Congruence and Similarity": ["Criteria for triangles", "Proving figures congruent or similar"],
    "Pythagorean Theorem": ["Derivation", "Applications in different contexts"],
    "Circles": ["Properties", "Arc length", "Sector area", "Theorems involving tangents and chords"],
    "Area and Volume": ["Formulas for various shapes", "Surface area and volume of 3D figures"],
    "Coordinate Geometry": ["Equation of a line", "Distance formula", "Midpoint formula"],
    # Trigonometry
    "Trigonometry": ["Introduction to sine", "Cosine", "Tangent", "Solving right triangles"],
    "Trigonometric Ratios": ["Definitions", "Solving for unknown sides or angles in right triangles"],
    "Graphs of Trigonometric Functions": ["Understanding amplitude", "Period", "Phase shift"],
    "Trigonometric Identities": ["Pythagorean", "Sum and difference", "Double-angle", "Half-angle formulas"],
    "Applications": ["Real-world problems", "Wave motion", "Circular motion"],
    # Statistics and Probability
    "Descriptive Statistics": ["Measures of central tendency", "Measures of dispersion", "Box plots"],
    "Probability Basics": ["Sample space", "Event probability", "Compound events", "Independent and dependent events"],
    "Combinations and Permutations": ["Calculating factorial", "Arrangements", "Choosing elements from a set"],
    "Random Variables and Distributions": ["Understanding discrete and continuous random variables", "Normal distribution"],
    "Inferential Statistics": ["Basic concepts of hypothesis testing", "Confidence intervals"],
    # Pre-Calculus
    "Advanced Algebra": ["Polynomial division", "Synthetic division", "Rational expressions"],
    "Complex Numbers": ["Operations", "Polar form", "De Moivre's Theorem"],
    "Exponential and Logarithmic Functions": ["Properties", "Solving exponential and logarithmic equations"],
    "Advanced Trigonometry": ["Solving general trigonometric equations", "Inverse trigonometric functions"],
    "Sequences and Series": ["Arithmetic and geometric sequences", "Sums", "Introduction to infinite series"],
    "Matrices": ["Operations", "Determinants", "Inverse of a matrix", "Applications in solving systems"],
    # Calculus
    "Limits": ["Concept of a limit", "Finding limits graphically and numerically", "Limit laws"],
    "Derivatives": ["Definition", "Techniques of differentiation", "Applications to motion and optimization"],
    "Integration": ["Antiderivatives", "Definite integrals", "The Fundamental Theorem of Calculus", "Area under a curve"],
    # Advanced Calculus
    "Series and Sequences": ["Taylor and Maclaurin series", "Convergence tests", "Applications"],
    "Vector Calculus": ["Vector functions", "Derivatives and integrals of vector functions", "Line and surface integrals"],
    "Multivariable Calculus": ["Partial derivatives", "Double and triple integrals"],
    "Differential Equations": ["Basic types and solutions", "Applications to growth and decay problems"],
    "Special Topics": ["Greens Theorem", "Stokes Theorem", "Divergence Theorem"],
    # Discrete Mathematics
    "Logic and Proofs": ["Propositional logic", "Predicate logic", "Methods of proof"],
    "Set Theory": ["Basic concepts", "Venn diagrams", "Operations on sets"],
    "Combinatorics": ["Advanced counting techniques", "Binomial theorem", "Generating functions"],
    "Graph Theory": ["Graphs and their properties", "Eulerian and Hamiltonian paths", "Graph coloring"],
    "Algorithms and Complexity": ["Algorithm design", "Complexity classes", "Big O notation"],
    # Linear Algebra
    "Vector Spaces": ["Definitions and properties", "Subspaces", "Basis and dimension"],
    "Linear Transformations": ["Matrix representation", "Geometric transformations"],
    "Advanced Matrices": ["Operations", "Special Matrices", "Inverses", "Matrix Equations", "Eigenvalues", "Factorization", "Rank", "Norms", "Exponentiation", "Applications"],
    "Systems of Linear Equations": ["Solution methods", "Applications"],
    "Advanced Topics": ["Orthogonality", "Least squares", "Singular value decomposition"],
    # Advanced Statistics
    "Regression Analysis": ["Simple and multiple linear regression", "Model fitting"],
    "ANOVA": ["Single-factor and multi-factor ANOVA"],
    "Nonparametric Tests": ["Chi-square tests", "Mann-Whitney U test", "Kruskal-Wallis test"],
    "Time Series Analysis": ["Components of time series", "ARIMA models"],
    "Bayesian Statistics": ["Bayesian inference", "Bayes' theorem"],
    # Mathematical Proofs and Theory
    "Introduction to Proofs": ["Logic and set theory based proofs", "Direct and indirect proofs"],
    "Number Theory": ["Prime numbers", "Modular arithmetic", "Fermat's Little Theorem"],
    "Group Theory": ["Basic properties of groups", "Subgroups", "Cyclic groups"],
    "Real Analysis": ["Sequences and series of real numbers", "Continuity", "Differentiability"],
    "Topology": ["Basic concepts", "Topological spaces", "Continuity", "Compactness"]
}


subsubsub_topics = {
    # Arithmetic Recognizing Shapes
    "Basic Shapes": ["Square", "Circle", "Triangle"],
    "Symmetry": ["Line (Reflective)", "Rotational", "Counting Lines of Symmetry"],
    # Arithmetic Number Sense
    "Counting": ["Count Forwards", "Count Backwards"],
    "Comparisons": ["Equality", "Less Than", "Greater Than"],
    # Arithmetic Basic Operations
    "Addition": ["Addends", "Sums", "Carries"], 
    "Subtraction": ["Minuend", "Subtrahend", "Difference", "Borrows"],
    "Multiplication": ["Multiplicand", "Multiplier", "Product", "Factors","Repeated Addition"],
    "Division": ["Dividend", "Divisor", "Quotient", "Remainder"],
    "Zero": ["Absence of Quantity", "Add/Sub Unchanged","Mpy is 0", "Divide is Undefined"], 
    "Operations Order": ["PEDMAS", "BODMAS"],
    # Arithmetic Number Properties
    "Odd and Even": ["Division by 2","Addition by 1 and 2", "Multiplication by 2"],
    "Prime": ["Definition", "Identification"],
    # Arithmetic Laws
    "Associative": ["Definition", "Grouping Numbers", "Add/Mpy", "Not Sub/Div"],
    "Commutative": ["Definition", "Operation Order", "Add/Mpy", "Not Sub/Div"],
    "Distributive" :["Definition", "Formula", "Multiplication", "Division Differences"],
    # Arithmetic Place Value
    "Units": ["Digit Dependence", "Digit Position", "Names (tens, hundreds, etc.)"], 
    "Writing Large Numbers": ["Base 10 Value System", "Use of Commas", "Periods (thousands, millions)"],
    # Arithmetic Time and Calendar
    "Reading Clocks": ["Analog","Digital","Hand Positions", "AM/PM"],
    "Measuring Time": ["Units", "Elapsed Time", "Difference between Times"],
    "Calendar Skills": ["Structure", "Reading", "Leap Years", "Non-Western Calendars"],
    # Arithmetic Fractions
    "Understanding": ["Part of Whole", "Numerator", "Denominator", "Mixed Numbers", "Improper"],
    "Simplifying": ["Equivalent", "GCD", "Simplist Form"],
    "Operations": ["Add", "Subtract", "Multiply", "Divide", "Compare"],
    # Arithmetic Money
    "Coins and Bills": ["Identification", "Relative Value", "Counting"],
    "Basic Transactions": ["Cost of Items", "Computing Change"],
    "Budgeting": ["Income", "Expenses", "Savings"],
    # Arithmetic Estimation and Rounding
    "Nearest decimal": ["Up/Down based on digits"], 
    "Estimate Operations": ["Approximate Basic Operations"],
    # Arithmetic Negative Numbers
    "Concept": ["Less than zero"], 
    "Number Line": ["Visualize"],
    "Basic Operations": ["Add", "Subtract", "Multiply", "Divide", "Combining Positive and Negative"],
    "Temperatures": ["Below Freezing"], 
    "Debt": ["Amount Owed", "Net Worth"],
    # Arithmetic Absolute Value
    "Number Line": ["Visualize"], 
    "Distance from Zero": ["Always Positive or Zero"],
    # Arithmetic Decimals
    "Conversion": ["Convert to Fraction"], 
    "Operations": ["Add", "Subtract", "Multiply", "Divide", "Align Decimal Points"],
    # Arithmetic Factors and Multiples
    "Finding Factors": ["No Remainder"], 
    "Common Multiples": ["List Multiples", "Identify Common"], 
    "GCF": ["List Factors", "Identify Common"], 
    "LCM": ["Divide Product by GCF"],
    # Arithmetic Exponents and Square Roots
    "Exponentiation as Repeated Multiplication": ["Repeated Self Multiplication", "Notation"], 
    "Square Roots": ["Perfect Squares", "Non-perfect Squares"],
    # Arithmetic Percentages
    "Calculating percentages": ["Fraction of 100", "Compute Percent"], 
    "Percentage increase/decrease": ["Percent Change Formula"], 
    "Real-world applications": ["Shopping Discounts", "Tips", "Taxes"],
    # Arithmetic Ratios and Proportions
    "Understanding ratios": ["Division of Quantities", "Notation"], 
    "Solving proportion problems": ["Equal Ratios", "Solving for Unknown"], 
    "Direct and inverse variation": ["Increase/Decrease at Same Rates", "Opposite Rates"],
    # Arithmetic Measurements and Units
    "Standard Units": ["Feet", "Pounds", "Yards", "Gallons"], 
    "Metric Units": ["Meters", "Kilograms", "Liters"], 
    "Converting Units": ["Length", "Weight", "Volume"] ,
    # Arithmetic Basic Graphs
    "Pictograph": ["Data as Symbols", "Legend"], 
    "Line graph": ["Series of Data Points", "Interpret Trends"],
    # Arithmetic Patterns and Sequences
    "Arithmetic Sequences": ["Constant Difference", "Extend a Sequence"],
    #########################################
    # ALGEBRA
    #########################################
        # Algebraic Expressions
    "Simplifying": ["Combine Like Terms", "Use Algebraic Properties", "Apply Order of Operations"],
    "Evaluating Expressions": ["Substitute Values", "Calculate Results", "Use of Variables"],
    "Combining Like Terms": ["Identify Like Terms", "Summing Coefficients", "Simplifying Polynomials"],

    # Linear Equations
    "Solving One-Variable": ["Isolate Variable", "Use Inverse Operations", "Check Solutions"],
    "Multi-Variable Equations": ["Solve Systems of Equations", "Use Elimination", "Use Substitution"],
    "Word Problems": ["Translate Words to Equations", "Interpret Results", "Solve Real-Life Problems"],

    # Inequalities
    "Solving": ["Isolate Variable", "Consider Inequality Direction", "Solution Sets"],
    "Graphing on a Number Line": ["Represent Inequalities", "Use Open/Closed Circles", "Shade Solution Regions"],
    "Compound Inequalities": ["Intersecting Solutions", "Combining Solution Sets", "Graphical Representation"],

    # Polynomials
    "Adding": ["Sum Like Terms", "Combine Polynomial Expressions", "Simplify Results"],
    "Subtracting": ["Subtract Polynomial Terms", "Rearrange Terms", "Simplify Expressions"],
    "Multiplying": ["Use Distributive Property", "Apply FOIL Method", "Expand Products"],
    "Dividing": ["Long Division of Polynomials", "Synthetic Division", "Remainder Theorem"],
    "Polynomial Long Division": ["Divide by Monomials", "Divide by Binomials", "Quotient and Remainder"],

    # Systems of Equations
    "Methods of Solving": ["Graphical Solution", "Algebraic Solution", "Comparison Method"],
    "Applications": ["Real-Life Problems", "Word Problems", "Modeling with Systems"],

    # Functions
    "Notation": ["Function Definition", "Function Evaluation", "Independent and Dependent Variables"],
    "Domain and Range": ["Determine Domain", "Determine Range", "Function Behavior Analysis"],
    "Inverse Functions": ["Find Inverse Functions", "Function Inversion Properties", "Graphical Representation"],

    # Quadratic Equations
    "Factoring": ["Factor Common Terms", "Factor Trinomials", "Factor by Grouping"],
    "Quadratic Formula": ["Derive Formula", "Solve Quadratic Equations", "Discriminant Analysis"],
    "Completing the Square": ["Square Completion Technique", "Vertex Finding", "Converting to Vertex Form"],
    "Graphing Parabolas": ["Identify Vertex", "Find Axis of Symmetry", "Plot Intercepts"],

    ################################
    # Geometry
    ################################
       # Basic Geometric Shapes
    "Properties of Triangles": ["Angle Sum Property", "Types of Triangles", "Congruence in Triangles"],
    "Quadrilaterals": ["Properties of Special Quadrilaterals", "Area and Perimeter", "Angle Properties"],
    "Polygons": ["Regular and Irregular Polygons", "Angle Sum in Polygons", "Properties of Polygons"],

    # Congruence and Similarity
    "Criteria for Triangles": ["SSS", "SAS", "ASA", "AAS"],
    "Proving Figures Congruent or Similar": ["Triangle Congruence Proofs", "Similarity in Geometric Shapes"],

    # Pythagorean Theorem
    "Derivation": ["Geometric Proof", "Algebraic Proof"],
    "Applications in Different Contexts": ["Problem Solving", "Real World Applications"],

    # Circles
    "Properties": ["Radius, Diameter, and Circumference", "Central and Inscribed Angles"],
    "Arc Length": ["Formula for Arc Length", "Applications in Geometry"],
    "Sector Area": ["Calculating Sector Area", "Real-World Applications"],
    "Theorems Involving Tangents and Chords": ["Properties of Tangents", "Chord Theorems"],

    # Area and Volume
    "Formulas for Various Shapes": ["Area of 2D Shapes", "Perimeter and Circumference"],
    "Surface Area and Volume of 3D Figures": ["Prisms and Cylinders", "Pyramids and Cones", "Spheres"],

    # Coordinate Geometry
    "Equation of a Line": ["Slope-Intercept Form", "Point-Slope Form", "Standard Form"],
    "Distance Formula": ["Calculating Distance Between Points", "Applications in Geometry"],
    "Midpoint Formula": ["Finding Midpoints", "Applications in Geometric Constructions"],
 
    ################################
    # Trigonometry
    ################################
    # Introduction to Trigonometry
    "Introduction to Sine": ["Definition", "Sine in Right Triangles", "Applications"],
    "Cosine": ["Definition", "Cosine in Right Triangles", "Applications"],
    "Tangent": ["Definition", "Tangent in Right Triangles", "Applications"],
    "Solving Right Triangles": ["Using Trigonometric Ratios", "Applications in Real Life", "Problem Solving Strategies"],

    # Trigonometric Ratios
    "Definitions": ["Sine, Cosine, Tangent", "Cosecant, Secant, Cotangent", "Trigonometric Ratios of Special Angles"],
    "Solving for Unknown Sides or Angles in Right Triangles": ["Using Inverse Trigonometric Functions", "Applications in Problem Solving"],

    # Graphs of Trigonometric Functions
    "Understanding Amplitude": ["Definition of Amplitude", "Effects on Graphs"],
    "Period": ["Definition of Period", "Determining Period of Functions"],
    "Phase Shift": ["Understanding Phase Shift", "Graphical Representation"],

    # Trigonometric Identities
    "Pythagorean": ["Sine and Cosine Pythagorean Identity", "Tangent and Cotangent Pythagorean Identity"],
    "Sum and Difference": ["Formulas for Sine and Cosine", "Applications"],
    "Double-Angle Formulas": ["Sine, Cosine, Tangent Double-Angle Identities", "Applications"],
    "Half-Angle Formulas": ["Sine, Cosine, Tangent Half-Angle Identities", "Applications"],

    # Applications
    "Real-World Problems": ["Angles of Elevation and Depression", "Navigation and Surveying"],
    "Wave Motion": ["Modeling Waves with Trigonometric Functions", "Amplitude and Frequency"],
    "Circular Motion": ["Uniform Circular Motion", "Relationship with Trigonometric Functions"],

    #################################
    # Statistics and Probability
    #################################
       # Descriptive Statistics
    "Measures of Central Tendency": ["Mean", "Median", "Mode", "Comparing Measures"],
    "Measures of Dispersion": ["Range", "Variance", "Standard Deviation", "Interquartile Range"],
    "Box Plots": ["Creating Box Plots", "Interpreting Box Plots", "Outliers Identification"],

    # Probability Basics
    "Sample Space": ["Definition", "Listing Outcomes", "Tree Diagrams"],
    "Event Probability": ["Calculating Probabilities", "Probability Rules", "Theoretical vs Experimental Probability"],
    "Compound Events": ["Addition Rule", "Multiplication Rule", "Complementary Events"],
    "Independent and Dependent Events": ["Understanding Independence", "Probability of Dependent Events", "Conditional Probability"],

    # Combinations and Permutations
    "Calculating Factorial": ["Definition", "Calculations", "Applications"],
    "Arrangements": ["Permutations", "Permutations with Repetition", "Circular Permutations"],
    "Choosing Elements from a Set": ["Combinations", "Applications", "Differences Between Combinations and Permutations"],

    # Random Variables and Distributions
    "Understanding Discrete and Continuous Random Variables": ["Definition", "Examples", "Probability Distributions"],
    "Normal Distribution": ["Characteristics", "Standard Normal Distribution", "Applications"],

    # Inferential Statistics
    "Basic Concepts of Hypothesis Testing": ["Null and Alternative Hypotheses", "Type I and II Errors", "Test Statistic"],
    "Confidence Intervals": ["Calculating Intervals", "Interpretation", "Margin of Error"],

    ##########################################
    # Pre-Calculus
    ##########################################
       # Advanced Algebra
    "Polynomial Division": ["Long Division of Polynomials", "Remainder Theorem", "Applications"],
    "Synthetic Division": ["Process of Synthetic Division", "Roots of Polynomials", "Using Synthetic Division for Simplification"],
    "Rational Expressions": ["Simplifying Rational Expressions", "Operations with Rational Expressions", "Complex Fractions"],

    # Complex Numbers
    "Operations": ["Addition and Subtraction", "Multiplication", "Division", "Complex Conjugates"],
    "Polar Form": ["Converting to Polar Form", "Multiplication and Division in Polar Form"],
    "De Moivre's Theorem": ["Statement and Proof", "Applications", "Finding Roots of Complex Numbers"],

    # Exponential and Logarithmic Functions
    "Properties": ["Laws of Exponents", "Properties of Logarithms"],
    "Solving Exponential and Logarithmic Equations": ["Transforming Equations", "Application Problems", "Graphical Methods"],

    # Advanced Trigonometry
    "Solving General Trigonometric Equations": ["Linear Trigonometric Equations", "Quadratic Trigonometric Equations"],
    "Inverse Trigonometric Functions": ["Defining Inverse Functions", "Properties and Graphs", "Applications and Problem Solving"],

    # Sequences and Series
    "Arithmetic and Geometric Sequences": ["Finding Terms", "General Formulas", "Real-World Applications"],
    "Sums": ["Summation Notation", "Summing Arithmetic and Geometric Series", "Partial Sums"],
    "Introduction to Infinite Series": ["Convergence and Divergence", "Geometric Series", "Basic Tests for Convergence"],

    # Matrices
    "Operations": ["Matrix Addition and Subtraction", "Scalar Multiplication", "Matrix Multiplication"],
    "Determinants": ["Calculating Determinants", "Properties", "Cramer's Rule"],
    "Inverse of a Matrix": ["Finding Inverse Matrices", "Properties", "Applications"],
    "Applications in Solving Systems": ["Using Matrices to Solve Linear Systems", "Applications in Real Life", "Matrix Algebra"],

    ###################################
    # Calculus
    ###################################
    # Limits
    "Concept of a Limit": ["Definition", "Intuitive Understanding", "Visualizing Limits"],
    "Finding Limits Graphically and Numerically": ["Using Graphs", "Limit Estimations", "Limit Tables"],
    "Limit Laws": ["Properties of Limits", "Simplifying Limits", "Special Cases (e.g., indeterminate forms)"],

    # Derivatives
    "Definition of Derivative": ["Tangent Line Interpretation", "Limits Definition", "Notation and Terminology"],
    "Techniques of Differentiation": ["Basic Rules (Power, Product, Quotient, Chain)", "Implicit Differentiation", "Higher Order Derivatives"],
    "Applications to Motion and Optimization": ["Velocity and Acceleration", "Optimization Problems", "Related Rates"],

    # Integration
    "Antiderivatives": ["Basic Techniques", "Initial Conditions", "Indefinite Integrals"],
    "Definite Integrals": ["Properties", "Calculation Techniques", "Interpretation"],
    "The Fundamental Theorem of Calculus": ["First and Second Part", "Relationship Between Derivatives and Integrals"],
    "Area under a Curve": ["Geometric Interpretation", "Applications", "Using Definite Integrals"],

 
 
    ###################################
    # Advanced Calculus
    ###################################

    # Series and Sequences
    "Taylor and Maclaurin Series": ["Formulation of Taylor Series", "Special Case of Maclaurin Series", "Applications and Approximations"],
    "Convergence Tests": ["Ratio Test", "Root Test", "Integral Test", "Comparison Tests"],
    "Applications of Series": ["Problem Solving with Series", "Series in Differential Equations", "Fourier Series"],

    # Vector Calculus
    "Vector Functions": ["Parametric Equations", "Graphing Vector Functions", "Motion in Space"],
    "Derivatives and Integrals of Vector Functions": ["Velocity and Acceleration Vectors", "Arc Length and Curvature", "Line Integrals"],
    "Line and Surface Integrals": ["Evaluating Line Integrals", "Surface Integrals", "Applications in Physics and Engineering"],

    # Multivariable Calculus
    "Partial Derivatives": ["Concept and Calculation", "Geometric Interpretation", "Higher Order Partial Derivatives"],
    "Double and Triple Integrals": ["Setting up Double Integrals", "Applications", "Triple Integrals and Applications"],

    # Differential Equations
    "Basic Types and Solutions": ["Separable Equations", "Linear Equations", "Exact Equations"],
    "Applications to Growth and Decay Problems": ["Exponential Growth and Decay", "Modeling with Differential Equations", "Population Dynamics"],

    # Special Topics in Advanced Calculus
    "Greens Theorem": ["Statement and Proof", "Applications in Plane", "Curl and Circulation"],
    "Stokes Theorem": ["Understanding Stokes' Theorem", "Applications in 3D", "Relation to Curl"],
    "Divergence Theorem": ["Gauss's Divergence Theorem", "Applications", "Flux through a Surface"],

    ##########################################
    # Discrete Math
    ##########################################
       # Logic and Proofs
    "Propositional Logic": ["Truth Tables", "Logical Connectives", "Tautologies and Contradictions"],
    "Predicate Logic": ["Quantifiers", "Logical Equivalences", "Predicates and Statements"],
    "Methods of Proof": ["Direct Proof", "Indirect Proof", "Proof by Contradiction", "Mathematical Induction"],

    # Set Theory
    "Basic Concepts": ["Elements and Subsets", "Universal Set", "Empty Set"],
    "Venn Diagrams": ["Representing Sets", "Set Relationships", "Applications in Solving Problems"],
    "Operations on Sets": ["Union", "Intersection", "Difference", "Complement"],

    # Combinatorics
    "Advanced Counting Techniques": ["Pigeonhole Principle", "Permutations and Combinations", "Inclusion-Exclusion Principle"],
    "Binomial Theorem": ["Expansion", "Binomial Coefficients", "Applications in Algebra"],
    "Generating Functions": ["Definition and Construction", "Applications in Counting", "Solving Recurrences"],

    # Graph Theory
    "Graphs and Their Properties": ["Types of Graphs", "Connectivity", "Trees and Spanning Trees"],
    "Eulerian and Hamiltonian Paths": ["Euler's Theorem", "Finding Eulerian Paths", "Hamiltonian Cycles"],
    "Graph Coloring": ["Coloring Algorithms", "Applications", "Chromatic Number"],

    # Algorithms and Complexity
    "Algorithm Design": ["Sorting Algorithms", "Search Algorithms", "Optimization Problems"],
    "Complexity Classes": ["P, NP, NP-Complete", "Computational Complexity", "Reduction"],
    "Big O Notation": ["Time Complexity Analysis", "Space Complexity", "Asymptotic Analysis"],
 
    ##########################################
    # Linear Algebra
    ##########################################
    # Vector Spaces
    "Definitions and Properties": ["Vector Operations", "Vector Space Axioms", "Examples of Vector Spaces"],
    "Subspaces": ["Definition and Properties", "Criteria for Subspaces", "Examples"],
    "Basis and Dimension": ["Definition of Basis", "Finding a Basis", "Dimension of Vector Spaces"],

    # Matrices
    "Operations": ["Matrix Addition and Subtraction", "Scalar Multiplication", "Matrix Multiplication", "Transposition"],
    "Special Matrices": ["Identity Matrix", "Zero Matrix", "Diagonal Matrix", "Symmetric Matrix", "Skew-Symmetric Matrix", "Orthogonal Matrix"],
    "Inverses": ["Invertible Matrices (Non-Singular)", "Determinants and Inverses", "Finding Matrix Inverses"],
    "Matrix Equations": ["Systems of Linear Equations as Matrices", "Matrix Equation AX = B", "Solving Linear Systems Using Matrices"],
    "Eigenvalues": ["Eigenvalues and Eigenvectors of a Matrix", "Diagonalization of Matrices", "Applications in Linear Transformations"],
    "Factorization": ["LU Decomposition", "QR Decomposition", "Singular Value Decomposition (SVD)"],
    "Rank": ["Rank of a Matrix", "Null Space (Kernel) of a Matrix", "Rank-Nullity Theorem"],
    "Norms": ["Norms of Matrices", "Condition Number of a Matrix", "Sensitivity of Solutions"],
    "Exponentiation": ["Exponentiating a Matrix", "Applications in Differential Equations"],
    "Applications": ["Linear Transformations", "Markov Chains", "Least Squares Approximations", "Principal Component Analysis (PCA)"],


    # Linear Transformations
    "Matrix Representation": ["Linear Transformations as Matrices", "Matrix Operations", "Change of Basis"],
    "Geometric Transformations": ["Rotation", "Scaling", "Reflection", "Shear Transformations"],

    # Systems of Linear Equations
    "Solution Methods": ["Gaussian Elimination", "Matrix Inversion", "Graphical Interpretation"],
    "Applications": ["Solving Real-world Problems", "Linear Programming", "Network Flow Problems"],

    # Advanced Topics
    "Orthogonality": ["Orthogonal Vectors and Subspaces", "Orthogonal Projections", "Gram-Schmidt Process"],
    "Least Squares": ["Method of Least Squares", "Applications in Data Fitting", "Regression Analysis"],
    "Singular Value Decomposition": ["Concept and Computation", "Applications", "Connection with Eigenvalues and Eigenvectors"],

    #####################################
    # Advanced Statistics
    #####################################
    # Regression Analysis
    "Simple and Multiple Linear Regression": ["Model Development", "Parameter Estimation", "Interpretation of Coefficients"],
    "Model Fitting": ["Goodness of Fit", "Residual Analysis", "Predictive Power of the Model"],

    # ANOVA (Analysis of Variance)
    "Single-Factor ANOVA": ["Between-Group Variability", "Within-Group Variability", "F-test"],
    "Multi-Factor ANOVA": ["Interaction Effects", "Main Effects", "ANOVA Table Interpretation"],

    # Nonparametric Tests
    "Chi-Square Tests": ["Goodness of Fit Test", "Test for Independence", "Homogeneity Test"],
    "Mann-Whitney U Test": ["Rank Sum Test", "Comparing Two Independent Samples"],
    "Kruskal-Wallis Test": ["One-Way ANOVA by Ranks", "Comparing More Than Two Independent Groups"],

    # Time Series Analysis
    "Components of Time Series": ["Trend", "Seasonality", "Cyclical", "Irregular Components"],
    "ARIMA Models": ["AutoRegressive (AR) Models", "Integrated (I) Models", "Moving Average (MA) Models", "Forecasting"],

    # Bayesian Statistics
    "Bayesian Inference": ["Prior Probability", "Likelihood", "Posterior Probability", "Updating Beliefs"],
    "Bayes' Theorem": ["Theorem Derivation", "Practical Applications", "Bayesian vs Frequentist Approach"],

    #####################################
    # Mathematical Proofs and Theory
    #####################################
    # Introduction to Proofs
    "Logic and Set Theory Based Proofs": ["Proof by Contradiction", "Proof by Contrapositive", "Proof by Cases"],
    "Direct and Indirect Proofs": ["Direct Proofs", "Indirect Proofs (Proof by Contradiction)", "Proofs Involving Quantifiers"],

    # Number Theory
    "Prime Numbers": ["Prime Factorization", "Properties of Prime Numbers", "Prime Counting Functions"],
    "Modular Arithmetic": ["Congruences", "Solving Modular Equations", "Applications in Cryptography"],
    "Fermat's Little Theorem": ["Statement and Proof", "Applications in Number Theory"],

    # Group Theory
    "Basic Properties of Groups": ["Group Definitions", "Group Operations", "Identity and Inverses"],
    "Subgroups": ["Definition and Properties", "Cyclic Subgroups", "Cosets and Lagrange's Theorem"],
    "Cyclic Groups": ["Definition and Properties", "Generators", "Applications in Group Theory"],

    # Real Analysis
    "Sequences and Series of Real Numbers": ["Convergence and Divergence", "Tests for Series Convergence", "Power Series"],
    "Continuity": ["Definition of Continuous Functions", "Intermediate Value Theorem", "Extreme Value Theorem"],
    "Differentiability": ["Definition of Derivative", "Mean Value Theorem", "Applications in Calculus"],

    # Topology
    "Basic Concepts": ["Open and Closed Sets", "Topological Spaces", "Neighborhoods"],
    "Topological Spaces": ["Definition and Properties", "Hausdorff Spaces", "Compactness and Connectedness"],
    "Continuity": ["Topology of Continuous Functions", "Homeomorphisms", "Applications in Geometry"]


}
