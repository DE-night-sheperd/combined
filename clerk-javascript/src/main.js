import { Clerk } from '@clerk/clerk-js'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!publishableKey) {
  throw new Error('Add your VITE_CLERK_PUBLISHABLE_KEY to the .env file')
}

// Derive the Frontend API domain from the publishable key
const clerkDomain = atob(publishableKey.split('_')[2]).slice(0, -1)

// Loads the Clerk UI bundle
await new Promise((resolve, reject) => {
  const script = document.createElement('script')
  script.src = `https://${clerkDomain}/npm/@clerk/ui@1/dist/ui.browser.js`
  script.async = true
  script.crossOrigin = 'anonymous'
  script.onload = resolve
  script.onerror = () => reject(new Error('Failed to load @clerk/ui bundle'))
  document.head.appendChild(script)
})

const clerk = new Clerk(publishableKey)
await clerk.load({
 ui: { ClerkUI: window.__internal_ClerkUICtor },
})

if (clerk.isSignedIn) {
  document.getElementById('app').innerHTML = `
    <div id="user-button"></div>
    <div id="portal-button" style="margin-top: 1rem">
      <button id="open-portal-button">Open Sentinel Grid Portal</button>
    </div>
  `
  const userButtonDiv = document.getElementById('user-button')
  clerk.mountUserButton(userButtonDiv)
  
  document.getElementById('open-portal-button').addEventListener('click', () => {
    window.location.href = '/sentinel_grid.html'
  })
} else {
  document.getElementById('app').innerHTML = `
    <div id="sign-in"></div>
  `
  const signInDiv = document.getElementById('sign-in')
  clerk.mountSignIn(signInDiv)
}
