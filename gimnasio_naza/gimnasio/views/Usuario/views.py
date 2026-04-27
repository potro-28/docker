from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from gimnasio.models import Usuario
from gimnasio.forms import UsuarioForm, UserForm


# =============================
# LISTAR USUARIOS
# =============================
class UsuarioListView(ListView):
    model = Usuario
    template_name = 'usuarios/listar.html'
    # Cambiado de 'usuarios' para que coincida con el template
    context_object_name = 'object_list'
    ordering = ['-id']

    def get_queryset(self):
        return Usuario.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Usuarios'
        context['crear_url'] = reverse_lazy(
            'gimnasio:crear_usuario')  # Sin el '2'
        return context


# =============================
# CREAR USUARIO
# =============================
class UsuarioCreateView(CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/crear.html'
    success_url = reverse_lazy('gimnasio:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST)
        else:
            context['user_form'] = UserForm()
        context['titulo'] = 'Crear Usuario'
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        usuario_form = self.get_form()
        user_form = UserForm(request.POST)
        if usuario_form.is_valid() and user_form.is_valid():
            return self.form_valid(usuario_form, user_form)
        else:
            return self.form_invalid(usuario_form, user_form)

    def form_valid(self, usuario_form, user_form):
        user = user_form.save(commit=False)
        user.set_password(user_form.cleaned_data['password'])
        user.save()
        usuario = usuario_form.save(commit=False)
        usuario.user = user
        usuario.estado = 'activo'
        usuario.save()
        messages.success(self.request, "Usuario Creado Correctamente")
        return redirect(self.success_url)
    def form_invalid(self, usuario_form,user_form):
        return self.render_to_response(self.get_context_data(form = usuario_form , user_form = user_form))

    

# =============================
# ACTUALIZAR USUARIO
# =============================
class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/crear.html'  # Usa el mismo template que crear
    success_url = reverse_lazy('gimnasio:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Usuario'
        usuario = self.object
        user = usuario.user
        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST,instance=user)
        else:
            context['user_form'] = UserForm(instance=user)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario_form = self.get_form()
        user_form = UserForm(request.POST, instance=self.object.user)
        if usuario_form.is_valid() and user_form.is_valid():
            return self.form_valid(usuario_form,user_form)
        else :
            return self.form_invalid(usuario_form,user_form)
    def form_valid(self,usuario_form,user_form):
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password')
        print(password)
        if password:
            user.set_password(password)
        user.save()
        usuario_form.save()
        messages.success(self.request,"Se Actualizo con exito")
        return super().form_valid(usuario_form)
    def form_invalid(self,usuario_form,user_form):
        return self.render_to_response(
            self.get_context_data(
                form = usuario_form,
                user_form = user_form
            )
        )
    

# =============================
# ELIMINAR USUARIO
# =============================
class UsuarioDeleteView(View):
    def post(self, request,pk):
        usuario = get_object_or_404(Usuario,pk=pk)
        usuario.user.is_active = not usuario.user.is_active
        usuario.user.save()
        usuario.estado = "activo" if usuario.user.is_active else "desactivo"
        usuario.save()
        estado = estado = "activado" if usuario.user.is_active else "desactivado"
        messages.success(request,f"Usuario {estado} correctamente")
        return redirect('gimnasio:listar_usuario')


# =============================
# ASIGNAR ROL A USUARIO
# =============================
class UsuarioRolUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/asignar_rol.html'
    success_url = reverse_lazy('gimnasio:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Asignar Rol'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Rol asignado correctamente")
        return super().form_valid(form)
    
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class PerfilView(LoginRequiredMixin, View):
    template_name = "Usuarios/perfil.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
        })