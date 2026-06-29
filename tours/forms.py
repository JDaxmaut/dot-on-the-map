from django import forms
from .models import ContactSubmission

_input_cls = (
    "w-full bg-transparent border-b border-bamboo-line py-3 text-[15px] font-light "
    "text-moss outline-none placeholder:text-muted-2 focus:border-terracotta "
    "transition-colors duration-300 font-sans"
)
_textarea_cls = (
    "w-full bg-transparent border-b border-bamboo-line py-3 text-[15px] font-light "
    "text-moss outline-none placeholder:text-muted-2 focus:border-terracotta "
    "transition-colors duration-300 font-sans resize-none"
)
_select_cls = (
    "w-full bg-transparent border-b border-bamboo-line py-3 text-[15px] font-light "
    "text-moss outline-none focus:border-terracotta transition-colors duration-300 font-sans"
)


class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactSubmission
        fields = ["name", "email", "phone", "tour", "message"]
        labels = {
            "name":    "Имя",
            "email":   "Email",
            "phone":   "Телефон",
            "tour":    "Интересующий маршрут",
            "message": "Сообщение",
        }
        widgets = {
            "name":    forms.TextInput(attrs={"class": _input_cls, "placeholder": "Анна Смирнова"}),
            "email":   forms.EmailInput(attrs={"class": _input_cls, "placeholder": "anna@example.com"}),
            "phone":   forms.TextInput(attrs={"class": _input_cls, "placeholder": "+7 999 000-00-00"}),
            "tour":    forms.TextInput(attrs={"class": _input_cls, "placeholder": "Бали, Япония или другое"}),
            "message": forms.Textarea(attrs={"class": _textarea_cls, "rows": 4,
                                             "placeholder": "Расскажите, что вас интересует…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required   = False
        self.fields["tour"].required    = False
        self.fields["message"].required = True
