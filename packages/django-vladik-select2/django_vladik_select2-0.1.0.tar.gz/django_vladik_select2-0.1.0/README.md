# django-vladik-select2

`django-vladik-select2` es una implementación de widgets **Select2** para Django, permitiendo cargar opciones dinámicamente mediante AJAX, manejar **selects dependientes** y ofrecer una integración simple con **Bootstrap 5**.

Este paquete nace como solución práctica cuando se necesitan selects que cambien según otros campos, sin recargar la página y con buen rendimiento.

---

## Características

- Compatible con Django >=3.8
- Integración mejorada con Bootstrap 5
- Soporte para dependencias dinámicas (`depend_*`)
- Carga remota mediante API / AJAX
- Compatible con formularios Django regulares y CBV
- Fácil de extender y personalizar

---
## Instalación

```python
pip install django-vladik-select2

```
## Modo de uso

```python
INSTALLED_APPS = [
    ...
    "django_vladik_select2",
]

urlpatterns = [
    ...
    path("vladik-select2/", include("django_vladik_select2.urls")),
]

from django_vladik_select2.widgets import Select2VladikWidget, DeferredModelChoiceField, apply_dependent_selects

class PersonaForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        widget=Select2VladikWidget(select_type='search', model_name='departamento')
    )

    provincia = DeferredModelChoiceField(
        queryset=Provincia.objects.none(),
        widget=Select2VladikWidget(select_type='search', model_name='provincia', depend='departamento')
    )

    distrito = DeferredModelChoiceField(
        queryset=Distrito.objects.none(),
        widget=Select2VladikWidget(select_type='source', model_name='distrito', depend='provincia')
    )

    etnia = DeferredModelChoiceField(
        queryset=Etnia.objects.all(),
        widget=Select2VladikWidget(select_type='simple', model_name='etnia', auto_load=True)
    )

    class Meta:
        model = Persona
        fields = ['nombre', 'departamento', 'provincia', 'distrito', 'etnia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_dependent_selects(self)

```
## Incluir en la plantilla(muy importante)
{{ form.media }}
