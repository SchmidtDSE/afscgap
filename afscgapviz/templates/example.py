import afscgap

results_1 = afscgap.query(
    survey='{{ survey }}',
    year={{ year }},
    {% if species %}scientific_name='{{ species }}'{% else %}common_name='{{ common_name }}'{% endif %},
    presence_only=False
)

{% if is_comparison %}
results_2 = afscgap.query(
    survey='{{ survey }}',
    year={{ other_year }},
    {% if other_species %}scientific_name='{{ other_species }}'{% else %}common_name='{{ other_common_name }}'{% endif %},
    presence_only=False
)
{% endif %}
