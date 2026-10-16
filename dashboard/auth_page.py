import streamlit as st

from auth.auth_service import login_user, register_user


def show_auth_page():
    st.title("🔐 Customer AI Analytics")
    st.subheader("Secure Analytics Platform")
    st.write("Login or create an account to access the platform.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.markdown("### Login")

        email = st.text_input(
            "Email",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button("Login", type="primary", use_container_width=True):
            success, result = login_user(email, password)

            if success:
                st.session_state["authenticated"] = True
                st.session_state["user"] = result
                st.rerun()
            else:
                st.error(result)

    with register_tab:
        st.markdown("### Create Account")

        name = st.text_input(
            "Full Name",
            key="register_name",
        )

        email = st.text_input(
            "Email",
            key="register_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password",
        )

        role = st.selectbox(
            "Account Type",
            ["customer", "admin"],
            key="register_role",
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True,
        ):
            success, message = register_user(
                name,
                email,
                password,
                role,
            )

            if success:
                st.success(message)
                st.info("You can now log in using your registered account.")
            else:
                st.error(message)