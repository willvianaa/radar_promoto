/* Login por e-mail e senha (até o SSO — Q-06). A senha só trafega no POST; nada fica guardado no navegador. */
import { esc } from "../util.js";
import { api, ErroApi } from "../api.js";

export function montar(el, { aoEntrar, msg }) {
  el.innerHTML = `<div class="login-box">
    <div class="brand"><div class="brand-logo" aria-hidden="true"><span>rt</span></div><div class="brand-name">Radar <b>Promotor</b></div><div class="brand-sub">RT Intelligence · P&amp;P</div></div>
    <form id="form-login" novalidate>
      <div id="login-msg" role="alert">${msg ? `<div class="banner">${esc(msg)}</div>` : ""}</div>
      <label class="f" for="l-email"><span>E-mail corporativo</span><input id="l-email" name="email" type="email" autocomplete="username" required inputmode="email"></label>
      <label class="f" for="l-senha"><span>Senha</span><input id="l-senha" name="senha" type="password" autocomplete="current-password" required></label>
      <button class="btn big" type="submit" id="l-ok">Entrar</button>
    </form>
    <p class="login-note">Uso restrito. Os acessos ficam registrados em auditoria.</p></div>`;
  const form = el.querySelector("#form-login");
  form.onsubmit = async (e) => {
    e.preventDefault();
    const email = form.email.value.trim(), senha = form.senha.value;
    const aviso = (t) => { el.querySelector("#login-msg").innerHTML = `<div class="banner err">${esc(t)}</div>`; };
    if (!email || !senha) return aviso("Informe e-mail e senha.");
    const b = el.querySelector("#l-ok"); b.disabled = true; b.textContent = "Entrando…";
    try {
      const u = await api.login(email, senha);
      form.senha.value = "";
      await aoEntrar(u);
    } catch (err) {
      form.senha.value = "";
      aviso(err instanceof ErroApi && err.status === 401 ? "E-mail ou senha inválidos." : "Não foi possível entrar agora. Tente de novo.");
    } finally { b.disabled = false; b.textContent = "Entrar"; }
  };
  const em = el.querySelector("#l-email"); if (em) em.focus();
}
