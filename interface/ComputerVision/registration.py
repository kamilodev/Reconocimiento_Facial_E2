"""New user registration form and validation logic."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import reflex as rx

from .base_state import State
from .login import LOGIN_ROUTE, REGISTER_ROUTE
# from .user import User
import re


import supabase
from dotenv import load_dotenv
from .css import style
import os

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.Client(supabase_url, supabase_key)

class RegistrationState(State):
    """Handle registration form submission and redirect to login page after registration."""

    success: bool = False
    error_message: str = ""

    is_loading: bool = False

    async def handle_registration(
        self, form_data
    ) -> AsyncGenerator[rx.event.EventSpec | list[rx.event.EventSpec] | None, None]:
        """Handle registration form on_submit.

        Set error_message appropriately based on validation results.

        Args:
            form_data: A dict of form fields and values.
        """

        # set the following values to spin the button
        self.is_loading = True
        yield


        email = form_data["email"]
        if not email:
            self.error_message = "El email no puede estar vacío."
            rx.set_focus("email")
            # reset state variable again
            self.is_loading = False
            yield
            return
        if not is_valid_email(email):
            self.error_message = "Esta no es una dirección de correo electrónico válida."
            rx.set_focus("email")
            # reset state variable again
            self.is_loading = False
            yield
            return

        password = form_data["password"]
        if not password:
            self.error_message = "El password no puede estar vacío."
            rx.set_focus("password")
            # reset state variable again
            self.is_loading = False
            yield
            return
        if password != form_data["confirm_password"]:
            self.error_message = "Los passwords no coinciden."
            [
                rx.set_value("confirm_password", ""),
                rx.set_focus("confirm_password"),
            ]
            # reset state variable again
            self.is_loading = False
            yield
            return

        # sign up with supabase
        supabase_client.auth.sign_up({
            "email": email,
            "password": password,
        })

        # Set success and redirect to login page after a brief delay.
        self.error_message = ""
        self.success = True
        self.is_loading = False
        yield
        await asyncio.sleep(3)
        yield [rx.redirect(LOGIN_ROUTE), RegistrationState.set_success(False)]


@rx.page(route=REGISTER_ROUTE)
def registration_page() -> rx.Component:
    """Render the registration page.

    Returns:
        A reflex component.
    """
    register_form = rx.form(
        rx.input(placeholder="email", id="email", type_="email", style=style.inputs_style),
        rx.password(placeholder="password", id="password", style=style.inputs_style),
        rx.password(placeholder="confirm", id="confirm_password", style=style.inputs_style),
        rx.button("Register", type_="submit", is_loading=RegistrationState.is_loading, style=style.button_style),
        
        style=style.form_style,
        on_submit=RegistrationState.handle_registration,
    )
    return rx.fragment(
        rx.cond(
            RegistrationState.success,
            rx.vstack(
                rx.text("Registro Exitoso!, revisa tu correo para activar tu cuenta."),
                rx.spinner(),
            ),
            rx.vstack(
                rx.cond(  # conditionally show error messages
                    RegistrationState.error_message != "",
                    rx.text(RegistrationState.error_message),
                ),
                register_form,
                rx.link("Login", href=LOGIN_ROUTE, color="#aeaeae"),
                padding_top="10vh",
                background="url(../background.svg)",
                background_repeat="repeat",
                height="100vh"
            ),
        )
    )

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None