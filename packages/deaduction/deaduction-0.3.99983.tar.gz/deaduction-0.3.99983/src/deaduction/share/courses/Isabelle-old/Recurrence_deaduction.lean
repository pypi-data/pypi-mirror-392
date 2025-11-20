/-
Feuille d'exercice pour travailler le raisonnement par récurrence sur N 
-/


import data.set
import tactic
import data.nat.basic
import data.real.basic


-- dEAduction imports
import structures2
import utils          
import push_neg_once
import compute          -- tactics for computation, used by the Goal! button
import induction



-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')


/- dEAduction
title = """
Démonstration par récurrence
-
"""
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = "Exercices sur la récurrence"
available_exercises = "NONE"
[display]
divise = [-2, " | ", -1]
-/


-- logic names ['and', 'or', 'not', 'implies', 'iff', 'forall', 'exists']
-- proofs names ['proof_methods', 'new_object', 'apply']
-- magic names ['compute', 'assumption']


local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
open nat


namespace recurrence



def pair (m: nat) := ∃ k, m = 2*k 

def impair (m: nat) := ∃ k, m = 2*k + 1 



lemma definition.pair {m:nat} : (pair m) ↔ ∃ k, m = 2*k :=
/- dEAduction
pretty_name = "Pair"
implicit_use = true
-/
begin
  todo
end

lemma definition.impair {m:nat} : (impair m) ↔ ∃ k, m = 2*k + 1 :=
/- dEAduction
pretty_name = "Impair"
implicit_use = true
-/
begin
  todo
end



lemma exercise.pair_ou_impair : ∀n: nat, (pair n ∨ impair n) :=
/- dEAduction
pretty_name = "Pair ou impair"
description = "Tout entier est pair ou impair, à démontrer par récurrence"
-/
begin
    todo
end

lemma theorem.puissance1  : ∀ a: ℤ , ∀ n: nat, a^(n+1) = (a^n)*a :=
/- dEAduction
pretty_name = "Propriété Puissance (Entiers relatifs)"
implicit_use = true
-/
begin
  todo
end

lemma theorem.puissance2  : ∀ x: ℝ , ∀ n: nat, x^(n+1) = (x^n)*x :=
/- dEAduction
pretty_name = "Propriété Puissance (Réels)"
implicit_use = true
-/
begin
  todo
end

lemma exercise.suite_arithmetico_geometrique {u : ℕ → ℤ} (H1 : u 0 = 3 ) (H2 :  ∀n: nat, u (n+1) = 3*(u n) - 2 ) : ∀n: nat, ( u n = 2 *( (3^n))+1 ):=
/- dEAduction
pretty_name = "Suite définie par récurrence arithmético-géométrique"
description = "Suite définie par récurrence de type arithmético-géométrique - Formule explicite à démontrer par récurrence"
available_definitions = "NONE"
available_theorems = "puissance1"
-/
begin
    todo
end




lemma exercise.suite_geometrique {p q : ℝ } {u : ℕ →  ℝ } (H1 : u 0 = p) (H2 :  ∀n: nat, u (n+1) = q*(u n) ) : ∀n: nat, ( u n = p *( q^n) ):=
/- dEAduction
pretty_name = "Suite définie par récurrence géométrique"
description = "Suite définie par récurrence de type géométrique - Formule explicite à démontrer par récurrence"
available_definitions = "NONE"
available_theorems = "puissance2"
-/
begin
    todo
end

def divise (a b:ℤ) := ∃ c, b = a * c

lemma definition.divise {a b : ℤ} : (divise a b) ↔ (∃ c, b = a * c) :=
/- dEAduction
pretty_name = "Divise"
implicit_use = true
-/
begin
  todo
end

lemma exercise.quatre_divise : ∀n: nat, divise (4) (3^n -(-1)^n) :=
/- dEAduction
pretty_name = "Divisibilité par 4"
description = "Divisibilité par 4 d'une expression dépendant de n,  à démontrer par récurrence"
available_definitions = "divise"
available_theorems = "puissance1"
 = """
"""
-/
begin
    todo
end

lemma theorem.puissance3  : ∀ m: nat , ∀ n: nat, m^(n+1) = (m^n)*m :=
/- dEAduction
pretty_name = "Propriété Puissance (Entiers naturels)"
implicit_use = true
-/
begin
  todo
end

lemma exercise.heredite_seule :  ( ∀n: nat, ( pair (3^n)  → pair (3^(n+1) ) ) ) and (∀n: nat, ( impair (3^n) )) :=
/- dEAduction
pretty_name = "Propriété héréditaire mais fausse"
description = "Propriété héréditaire mais qui est toujours fausse."
available_definitions = "pair, impair"
available_theorems = "puissance3"
-/
begin
    todo
end


end recurrence

end course
