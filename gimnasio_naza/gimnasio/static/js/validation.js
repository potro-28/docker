document.addEventListener("DOMContentLoaded", () => {

    const modal =
    document.getElementById("modalUsuario");

    const inputs =
    modal.querySelectorAll(
        ".form-control, .form-select"
    );

    inputs.forEach(input => {

        input.addEventListener(
            "input",
            () => validarCampo(input)
        );

        input.addEventListener(
            "change",
            () => validarCampo(input)
        );
    });

    modal.addEventListener(
        "hidden.bs.modal",
        () => {

            inputs.forEach(input => {

                input.classList.remove(
                    "is-invalid",
                    "is-valid"
                );

                const errorDiv =
                document.getElementById(
                    `error-${input.id}`
                );

                if(errorDiv){
                    errorDiv.remove();
                }

            });

        }
    );

});


function mostrarError(input,mensaje){

    input.classList.remove("is-valid");
    input.classList.add("is-invalid");

    let errorDiv =
    document.getElementById(
        `error-${input.id}`
    );

    if(!errorDiv){

        errorDiv =
        document.createElement("div");

        errorDiv.id =
        `error-${input.id}`;

        errorDiv.className =
        "invalid-feedback d-block text-start small fw-bold mt-1";

        errorDiv.style.fontSize =
        "11px";

        input.parentNode.appendChild(
            errorDiv
        );
    }

    errorDiv.textContent =
    mensaje;
}


function limpiarError(input){

    input.classList.remove(
        "is-invalid"
    );

    input.classList.add(
        "is-valid"
    );

    const errorDiv =
    document.getElementById(
        `error-${input.id}`
    );

    if(errorDiv){
        errorDiv.remove();
    }
}


function validarCampo(input){

    const id =
    input.id;

    const valor =
    input.value.trim();


    /* vacío */

    if(valor === ""){

        let nombre =
        id.replace(/_/g," ");

        mostrarError(
            input,
            `El campo "${nombre}" es obligatorio`
        );

        return false;
    }


    /* documento */

    if(
        id === "documento" &&
        !/^\d{7,10}$/.test(valor)
    ){

        mostrarError(
            input,
            "Debe tener entre 7 y 10 dígitos"
        );

        return false;
    }


    /* nombre */

    if(
        (
            id === "nombre" ||
            id === "apellido"
        )
        &&
        !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(valor)
    ){

        mostrarError(
            input,
            "Solo se permiten letras"
        );

        return false;
    }


    /* correo */

    if(
        id === "correo" &&
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor)
    ){

        mostrarError(
            input,
            "Correo electrónico inválido"
        );

        return false;
    }


    /* teléfono */

    if(
        id === "telefono" &&
        !/^3\d{9}$/.test(valor)
    ){

        mostrarError(
            input,
            "Debe iniciar en 3 y tener 10 dígitos"
        );

        return false;
    }


    /* username */

    if(
        id === "username" &&
        valor.length < 4
    ){

        mostrarError(
            input,
            "Mínimo 4 caracteres"
        );

        return false;
    }


    /* password */

    if(
        id === "password" &&
        valor.length < 6
    ){

        mostrarError(
            input,
            "Mínimo 6 caracteres"
        );

        return false;
    }


    /* peso */

    if(
        (
            id === "peso_usuario" ||
            id === "peso_cliente"
        )
        &&
        (
            Number(valor) < 30 ||
            Number(valor) > 200
        )
    ){

        mostrarError(
            input,
            "Peso fuera de rango"
        );

        return false;
    }


    /* altura */

    if(
        (
            id === "altura_usuario" ||
            id === "altura_cliente"
        )
        &&
        (
            Number(valor) < 100 ||
            Number(valor) > 250
        )
    ){

        mostrarError(
            input,
            "Altura fuera de rango"
        );

        return false;
    }


    /* fecha */

    if(
        id === "fecha_nacimiento"
    ){

        const fecha =
        new Date(valor);

        const hoy =
        new Date();

        if(fecha >= hoy){

            mostrarError(
                input,
                "Fecha inválida"
            );

            return false;
        }
    }


    /* select género */

    if(
        id === "genero" &&
        valor === ""
    ){

        mostrarError(
            input,
            "Selecciona una opción"
        );

        return false;
    }


    limpiarError(input);

    return true;
}

const passwordInput =
    document.getElementById(
        "password"
    );

const btnTogglePassword =
    document.getElementById(
        "btnTogglePassword"
    );

const iconPassword =
    document.getElementById(
        "iconPassword"
    );

if (
    btnTogglePassword
) {

    btnTogglePassword
        .addEventListener(
            "click",
            function () {

                const esPassword =
                    passwordInput.type ===
                    "password";

                passwordInput.type =
                    esPassword
                        ? "text"
                        : "password";

                iconPassword.className =
                    esPassword
                        ? "ri-eye-off-line"
                        : "ri-eye-line";
            }
        );
}