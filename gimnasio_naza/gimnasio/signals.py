from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from gimnasio.models import Usuario

@receiver(post_migrate)
def create_grupos(sender, **kwargs):
    grupos = ['Administrador', 'Cliente']
    for grupo in grupos:
        g, created = Group.objects.get_or_create(name=grupo)
        if g.name == 'Administrador':
            g.permissions.set(Permission.objects.all())
        elif g.name == 'Cliente':
            g.permissions.set(Permission.objects.filter(codename__in=[
                'add_usuario',
                'change_usuario',
                'view_usuario',
                'delete_usuario',
            ]))
        g.save()

@receiver(post_save, sender=Usuario)
def asignar_grupo_por_rol(sender, instance, **kwargs):
    """
    Asigna un grupo al usuario según el rol y sincroniza los permisos.
    """
    print(f"Guardando usuario '{instance.user.username}' con rol '{instance.rol}'")
    if instance.user:
        grupo, _ = Group.objects.get_or_create(name=instance.rol)
        if grupo.name == 'Administrador':
            grupo.permissions.set(Permission.objects.all())
        elif grupo.name == 'Cliente':
            grupo.permissions.set(Permission.objects.filter(codename__in=[
                'add_usuario',
                'change_usuario',
                'view_usuario',
                'delete_usuario',
            ]))
        grupo.save()
        print(f"Asignando grupo '{grupo.name}' al usuario '{instance.user.username}'")
        print(f"Permisos asignados al grupo '{grupo.name}': {[perm.codename for perm in grupo.permissions.all()]}")
        instance.user.groups.set([grupo])