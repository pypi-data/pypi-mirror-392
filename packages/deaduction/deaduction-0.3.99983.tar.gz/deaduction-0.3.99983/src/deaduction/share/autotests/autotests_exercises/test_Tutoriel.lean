/-
This is a d∃∀duction file providing easy and progressive exercises for basic set theory.
It may be used as a tutorial for d∃∀duction.
French version.
-/

-- Lean standard imports
import tactic
import data.real.basic

-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

-------------------------
-- dEAduction METADATA --
-------------------------

/- dEAduction
title = "Tutoriel"
author = "Camille Lichère"
institution = "Université de France"
description = """
Ce fichier contient quelques exercices faciles et progressifs de théorie élémentaire
des ensembles. Il peut être utilisé comme tutoriel pour d∃∀duction ; en particulier,
les boutons logiques sont introduits progressivement.
"""
default_available_logic = "ALL -not -exists -map -equal -iff"
available_proof = "ALL -new_object"
available_compute = "NONE"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = false
others.Lean_request_method = "normal"
-/

/- Notes for exercise makers.

List of buttons
AvailableLogic
    forall exists implies and or
    map equal iff not
AvailableProof
    proof_methods new_object
AvailableCompute
    sum transitivity commute associativity
    triangular_inequality simplify
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}

open set

------------------------
-- COURSE DEFINITIONS --
------------------------
namespace definitions
/- dEAduction
pretty_name = "Définitions"
-/

namespace inclusions_egalites
/- dEAduction
pretty_name = "Inclusions, égalités"
-/

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
implicit_use = true
-/
begin
    exact iff.rfl,
end

-- lemma definition.egalite_deux_ensembles {A A' : set X} :
-- (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
-- /- dEAduction
-- PrettyName
--     Egalité de deux ensembles
-- ImplicitUse
--     False
-- -/
-- begin
--      exact set.ext_iff,
-- end


lemma definition.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A):=
/- dEAduction
pretty_name = "Double inclusion"
implicit_use = true
-/
begin
    exact subset.antisymm_iff,
end
end inclusions_egalites

namespace unions_intersections
/- dEAduction
pretty_name = "Unions, intersections"
-/
lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
pretty_name = "Intersection de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl,
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
pretty_name = "Union de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl,
end

end unions_intersections

end definitions
---------------
-- SECTION 1 --
---------------
-- variables exercices --
-- variables {A B C : set X}


---------------
-- EXERCICES --
---------------
namespace exercices

lemma exercise.intersection_inclus_ensemble
(A B : set X) :
A ∩ B ⊆ A
:=
/- dEAduction
pretty_name = "Un ensemble contient son intersection avec un autre"
description = "Voici un premier exercice !"
-/
begin
    todo,
end

lemma exercise.intersection_inclus_ensemble_2 
(A B : set X) :
A ∩ B ⊆ A
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { target_selected = true, button = "prove_forall", success_msg = "Objet x ajouté au contexte" },
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "18nov.16h33"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_0,
--   cases H_0 with H_aux_0 H_aux_1, assumption, trace "EFFECTIVE CODE n°2.0", trace "EFFECTIVE CODE n°0.3",
  todo
end


lemma exercise.intersection_inclus_ensemble_1 
(A B : set X) :
A ∩ B ⊆ A
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { target_selected = true, button = "prove_forall", success_msg = "Objet x ajouté au contexte" },
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "18nov.16h27"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_0,
--   cases H_0 with H_aux_0 H_aux_1, assumption, trace "EFFECTIVE CODE n°2.0", trace "EFFECTIVE CODE n°0.3",
  todo
end



lemma exercise.inclus_dans_les_deux_implique_dans_lintersection
(A B C : set X) :
(C ⊆ A) ∧ (C ⊆ B) → C ⊆ A ∩ B
:=
/- dEAduction
pretty_name = "Inclus dans les deux implique inclus dans l'intersection"
description = "Voici un deuxième exercice !"
-/
begin
    todo,
end

lemma exercise.inclus_dans_les_deux_implique_dans_lintersection_1 
(A B C : set X) :
(C ⊆ A) ∧ (C ⊆ B) → C ⊆ A ∩ B
:=
/- dEAduction
all_goals_solved = "True"
history_date = "18nov.16h29"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_0 découpée en H_1 et H_2"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
selection = [ "@P3", "@P2" ]
button = "use_implies"
success_msg = "Propriété H_5 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4", "@P5" ]
button = "prove_and"
success_msg = "Conjonction H_6 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4" ]
statement = "definition.intersection_deux_ensembles"
success_msg = "Définition appliquée à H_6"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_0,
--   cases H_0 with H_1 H_2,
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_3,
--   have H_4 := H_1 H_3, trace "EFFECTIVE CODE n°4.0",
--   have H_5 := H_2 H_3, trace "EFFECTIVE CODE n°5.0",
--   have H_6 := and.intro H_4 H_5, clear H_4, clear H_5,
--   rw <- definitions.unions_intersections.definition.intersection_deux_ensembles at H_6, trace "EFFECTIVE CODE n°7.2", trace "EFFECTIVE CODE n°8.1", trace "EFFECTIVE CODE n°6.0",
--   assumption, trace "EFFECTIVE CODE n°10.0",
  todo
end


lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"
description = "Voici un troisième exercice !"
-/
begin
    todo,
end

lemma exercise.inclusion_transitive_1 
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
all_goals_solved = "True"
history_date = "18nov.16h33"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_0 découpée en H_1 et H_2"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4", "@P2" ]
button = "use_implies"
success_msg = "Propriété H_5 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_0,
--   cases H_0 with H_1 H_2,
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_3,
--   have H_4 := H_1 H_3, trace "EFFECTIVE CODE n°4.0",
--   have H_5 := H_2 H_4, trace "EFFECTIVE CODE n°5.0",
--   assumption, trace "EFFECTIVE CODE n°6.0",
  todo
end


lemma exercise.ensemble_inclus_union
(A B : set X) :
B ⊆ A ∪ B
:=
/- dEAduction
pretty_name = "Ensemble inclus dans l'union"
description = 'Le bouton ∨ ("ou"), permet notamment de montrer un but de la forme "P ou Q" en choisissant si on veut montrer "P" ou "Q".'
-/
begin
    todo,
end

lemma exercise.ensemble_inclus_union_1 
(A B : set X) :
B ⊆ A ∪ B
:=
/- dEAduction
all_goals_solved = "True"
history_date = "18nov.16h34"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
target_selected = true
button = "prove_or"
user_input = [
    1,
]
success_msg = "But remplacé par l’alternative de droite"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_0,
--   right,
--   assumption, trace "EFFECTIVE CODE n°0.0",
  todo
end


lemma exercise.ensemble_inclus_intersection
(A B : set X) :
A ⊆ A ∩ B  → (A ∪ B) = B
:=
/- dEAduction
pretty_name = "Ensemble inclus dans l'intersection"
description = """
Utilisez la double inclusion pour montrer une égalité entre ensembles.
Le bouton ∨ ("ou") permet également, appliqué à une hypothèse du type "P ou Q" de faire une disjonction de cas selon si on a "P" ou "Q".
"""
-/
begin
    todo,
end

lemma exercise.ensemble_inclus_intersection_1 
(A B : set X) :
A ⊆ A ∩ B  → (A ∪ B) = B
:=
/- dEAduction
all_goals_solved = "True"
history_date = "18nov.16h37"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
target_selected = true
button = "prove_and"
user_input = [
    0,
]
success_msg = "On décompose le but"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
selection = [ "@P2" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
selection = [ "@P2", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_3 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
target_selected = true
statement = "exercise.ensemble_inclus_union"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_0,
--   rw definitions.inclusions_egalites.definition.double_inclusion, split,
--   rw definitions.inclusions_egalites.definition.inclusion, intro x, intro H_1,
--   cases H_1 with H_2 H_3,
--   have H_3 := H_0 H_2, trace "EFFECTIVE CODE n°2.0",
--   cases H_3 with H_aux_0 H_aux_1, assumption, trace "EFFECTIVE CODE n°5.0", trace "EFFECTIVE CODE n°3.3",
--   assumption, trace "EFFECTIVE CODE n°7.0",
--   apply_with exercices.exercise.ensemble_inclus_union {md:=reducible},
  todo
end


lemma exercise.inter_distributive_union
(A B C : set X):
A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)
:=
/- dEAduction
pretty_name = "Union avec une intersection"
description = "Utilisez l'aperçu de preuve pour ne pas vous perdre dans les différents cas."
-/
begin
    todo,
end

lemma exercise.exercice_bilan
(A B : set X) :
A ⊆ B ↔ A ∩ B = A
:=
/- dEAduction
pretty_name = "Exercice bilan"
description = """
Dans cet exercice, deux nouveaux boutons apparaissent.
On peut utiliser une égalité pour remplacer l'un des termes par l'autre.
"""
available_logic = "ALL -not -exists -map"
-/
begin
    todo
end
end exercices

end course