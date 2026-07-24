
let ingredients = []
let recipeData  = []  
const API_URL   = 'http://localhost:3000/api'

// DOM refs
const uploadInput  = document.getElementById('imageUpload')
const previewImage = document.getElementById('previewImage')
const input        = document.getElementById('ingredientInput')
const auto         = document.getElementById('autocomplete')

let model



async function loadAI() {
  try {
    model = await cocoSsd.load()
    console.log('AI detection model loaded ✓')
  } catch(e) {
    console.warn('AI model failed to load', e)
  }
}
loadAI()


const ingredientDB = [
  'egg','milk','butter','cheese','bread','rice','pasta','tomato','onion',
  'potato','carrot','spinach','mushroom','capsicum','garlic','ginger',
  'chicken','fish','beef','paneer','yogurt','cream','flour','corn',
  'peas','cabbage','lettuce','broccoli','beans','soy sauce','vinegar',
  'salt','pepper','oil','sugar','honey','chili','turmeric','cumin',
  'lemon','lime','avocado','cucumber','zucchini','eggplant','celery',
  'bacon','sausage','shrimp','tofu','lentils','chickpeas','oats',
  'almond','walnut','peanut butter','coconut milk','apple','banana',
  'orange','strawberry','blueberry','mango','pineapple','grape',
  'cilantro','parsley','basil','thyme','rosemary','oregano','paprika',
  'cinnamon','nutmeg','cardamom','saffron','vanilla','cocoa','chocolate'
]

const ingredientEmojis = {
  egg: '🥚', milk: '🥛', butter: '🧈', cheese: '🧀', bread: '🍞',
  rice: '🍚', pasta: '🍝', tomato: '🍅', onion: '🧅', potato: '🥔',
  carrot: '🥕', spinach: '🥬', mushroom: '🍄', capsicum: '🫑',
  garlic: '🧄', ginger: '🫚', chicken: '🍗', fish: '🐟', beef: '🥩',
  corn: '🌽', lemon: '🍋', lime: '🍋', avocado: '🥑', cucumber: '🥒',
  eggplant: '🍆', apple: '🍎', banana: '🍌', orange: '🍊',
  strawberry: '🍓', blueberry: '🫐', mango: '🥭', pineapple: '🍍',
  chocolate: '🍫', coconut: '🥥', shrimp: '🍤',
}

function getEmoji(name) {
  return ingredientEmojis[name] || '🥄'
}


if (uploadInput) {
  uploadInput.addEventListener('change', function () {
    const file = this.files[0]
    if (!file) return

    const previewWrap = document.getElementById('aiPreviewWrap')
    const uploadZone  = document.getElementById('uploadZone')

    previewImage.src = URL.createObjectURL(file)
    if (previewWrap) previewWrap.style.display = 'flex'
    if (uploadZone)  uploadZone.style.display  = 'none'
  })
}

function retakePhoto() {
  const previewWrap = document.getElementById('aiPreviewWrap')
  const uploadZone  = document.getElementById('uploadZone')
  previewImage.src  = ''
  if (uploadInput) uploadInput.value = ''
  if (previewWrap) previewWrap.style.display = 'none'
  if (uploadZone)  uploadZone.style.display  = 'flex'
}


if (input) {
  input.addEventListener('input', function () {
    const value = this.value.toLowerCase().trim()
    auto.innerHTML = ''

    if (!value) return

    const matches = ingredientDB
      .filter(i => i.includes(value))
      .slice(0, 7)

    if (!matches.length) return

    matches.forEach(i => {
      const div = document.createElement('div')
      div.classList.add('suggestion')
      div.innerHTML = `${getEmoji(i)} ${i}`
      div.onclick = () => {
        input.value = i
        auto.innerHTML = ''
        addIngredient()
      }
      auto.appendChild(div)
    })
  })

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.big-search-wrap')) {
      auto.innerHTML = ''
    }
  })

  // Add on Enter key
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addIngredient()
    }
  })
}



function addIngredient() {
  const value = input.value.trim().toLowerCase()
  if (!value || ingredients.includes(value)) {
    input.value = ''
    auto.innerHTML = ''
    return
  }
  ingredients.push(value)
  input.value = ''
  auto.innerHTML = ''
  displayIngredients()
  updateFindBtn()
}

// Quick-add from chips
function quickAdd(name) {
  if (ingredients.includes(name)) return
  ingredients.push(name)
  displayIngredients()
  updateFindBtn()
}

// Clear all
function clearAllIngredients() {
  ingredients = []
  displayIngredients()
  updateFindBtn()
  // hide recipe section
  const rs = document.getElementById('recipesSection')
  if (rs) rs.style.display = 'none'
}



function displayIngredients() {
  const box = document.getElementById('selectedIngredients')
  if (!box) return
  box.innerHTML = ''

  ingredients.forEach((item, index) => {
    const tag = document.createElement('div')
    tag.classList.add('tag')
    tag.innerHTML = `
      <span>${getEmoji(item)}</span>
      <span>${item}</span>
      <button class="tag-remove" onclick="removeIngredient(${index})" aria-label="Remove ${item}">✕</button>
    `
    box.appendChild(tag)
  })
}



function removeIngredient(index) {
  ingredients.splice(index, 1)
  displayIngredients()
  updateFindBtn()
}

function updateFindBtn() {
  const wrap = document.getElementById('findRecipesWrap')
  if (!wrap) return
  wrap.style.display = ingredients.length > 0 ? 'flex' : 'none'
}



function showSkeletons(count = 6) {
  const container = document.getElementById('recipes')
  container.innerHTML = ''
  for (let i = 0; i < count; i++) {
    container.innerHTML += `
      <div class="skeleton-card">
        <div class="skeleton-img"></div>
        <div class="skeleton-lines">
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
          <div class="skeleton-line shorter"></div>
        </div>
      </div>`
  }
}



async function findRecipes() {
  if (ingredients.length === 0) return

  // Show recipes section
  const recipesSection = document.getElementById('recipesSection')
  if (recipesSection) {
    recipesSection.style.display = 'block'
    recipesSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  // Update subtitle
  const sub = document.getElementById('recipeSubtitle')
  if (sub) sub.innerText = `Based on: ${ingredients.join(', ')}`

  // Loading state
  const btn = document.getElementById('findRecipesBtn')
  const btnText = document.getElementById('findBtnText')
  if (btn) btn.disabled = true
  if (btnText) btnText.innerText = 'Searching…'
  showSkeletons(6)

  const ingredientString = ingredients.join(',')
  const url = `https://api.spoonacular.com/recipes/findByIngredients?ingredients=${ingredientString}&number=9&apiKey=f27dfecc2f80481bb246959ef390881b`

  try {
    const res  = await fetch(url)
    const data = await res.json()
    recipeData = data  // store for sorting

    renderRecipes(data)

    // Save history if logged in
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      fetch(`${API_URL}/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, search_term: ingredients.join(', ') })
      }).catch(e => console.error('History save error:', e))
    }
  } catch (e) {
    const container = document.getElementById('recipes')
    container.innerHTML = `
      <div class="empty-recipes" style="grid-column:1/-1">
        <div class="empty-recipes-icon">⚠️</div>
        <h3>Couldn't load recipes</h3>
        <p>Check your connection or try again.</p>
      </div>`
    console.error(e)
  } finally {
    if (btn) btn.disabled = false
    if (btnText) btnText.innerText = 'Find Recipes'
  }
}



function renderRecipes(data) {
  const container = document.getElementById('recipes')
  container.innerHTML = ''

  if (!data || data.length === 0) {
    container.innerHTML = `
      <div class="empty-recipes">
        <div class="empty-recipes-icon">🍳</div>
        <h3>No recipes found</h3>
        <p>Try adding different ingredients to get better results.</p>
      </div>`
    return
  }

  data.forEach((recipe, idx) => {
    const card = document.createElement('div')
    card.classList.add('recipe-card')
    card.style.animationDelay = `${idx * 0.06}s`

    const missing = recipe.missedIngredientCount || 0
    const used    = recipe.usedIngredientCount    || 0

    const escapedTitle = (recipe.title || '').replace(/'/g, "\\'")

    card.innerHTML = `
      <div class="recipe-card-img-wrap">
        <img src="${recipe.image}" alt="${recipe.title}" loading="lazy">
        <span class="recipe-card-badge">🍴 Recipe</span>
      </div>
      <div class="recipe-card-content">
        <h3>${recipe.title}</h3>
        <div class="recipe-card-meta">
          <span class="recipe-meta-pill">✅ ${used} used</span>
          ${missing > 0 ? `<span class="recipe-meta-pill recipe-missing-pill">➕ ${missing} missing</span>` : ''}
        </div>
        <div class="recipe-card-actions">
          <button class="recipe-view-btn" onclick="event.stopPropagation(); openRecipe(${recipe.id})">
            View Recipe →
          </button>
          <button class="recipe-save-btn" onclick="event.stopPropagation(); saveFavorite('${escapedTitle}', ${recipe.id}, '${recipe.image}')" title="Save to favorites">
            ⭐
          </button>
        </div>
      </div>`

    card.addEventListener('click', () => openRecipe(recipe.id))
    container.appendChild(card)
  })
}



function sortRecipes() {
  if (!recipeData.length) return
  const val  = document.getElementById('sortSelect').value
  let sorted = [...recipeData]

  if (val === 'alpha') {
    sorted.sort((a, b) => a.title.localeCompare(b.title))
  } else if (val === 'used') {
    sorted.sort((a, b) => b.usedIngredientCount - a.usedIngredientCount)
  }
  renderRecipes(sorted)
}



async function saveFavorite(recipeName, recipeId, imageUrl) {
  const userStr = localStorage.getItem('user')
  if (!userStr) {
    openProfile()
    return
  }

  const user = JSON.parse(userStr)
  try {
    const res  = await fetch(`${API_URL}/favorites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: user.id, recipe_name: recipeName, recipe_id: recipeId, image_url: imageUrl })
    })
    const data = await res.json()
    if (!res.ok) console.warn(data.error || 'Failed to save favorite')
  } catch (e) {
    console.error(e)
  }
}

function showFavorites() { openProfile() }



function showHistory() { openProfile() }



function toggleDark() {
  document.body.classList.toggle('dark')
  const btn = document.querySelector('#navDark .nav-icon')
  if (btn) btn.innerText = document.body.classList.contains('dark') ? '☀️' : '🌙'
}



let isSignup = false

function switchToLogin() {
  isSignup = false
  document.getElementById('loginTab').classList.add('active')
  document.getElementById('signupTab').classList.remove('active')
  document.getElementById('authTabIndicator').style.transform = 'translateX(0)'
  document.getElementById('emailField').style.display = 'none'
  document.getElementById('authFormTitle').innerText   = 'Welcome back!'
  document.getElementById('authFormSubtitle').innerText = 'Login to your FridgeChef account'
  document.getElementById('authBtnText').innerText     = 'Login'
  document.getElementById('toggleTextMsg').innerText  = "Don't have an account?"
  document.getElementById('toggleText').innerText     = 'Sign Up'
  clearAuthMsg()
}

function switchToSignup() {
  isSignup = true
  document.getElementById('signupTab').classList.add('active')
  document.getElementById('loginTab').classList.remove('active')
  document.getElementById('authTabIndicator').style.transform = 'translateX(calc(100% + 4rem))'
  document.getElementById('emailField').style.display = 'flex'
  document.getElementById('authFormTitle').innerText   = 'Create account'
  document.getElementById('authFormSubtitle').innerText = 'Join FridgeChef and start cooking!'
  document.getElementById('authBtnText').innerText     = 'Create Account'
  document.getElementById('toggleTextMsg').innerText  = 'Already have an account?'
  document.getElementById('toggleText').innerText     = 'Login'
  clearAuthMsg()
}

function toggleAuth() { isSignup ? switchToLogin() : switchToSignup() }

function togglePasswordVisibility() {
  const pwd = document.getElementById('password')
  const eye = document.getElementById('authEyeIcon')
  if (pwd.type === 'password') { pwd.type = 'text'; eye.innerText = '🙈' }
  else                         { pwd.type = 'password'; eye.innerText = '👁️' }
}

function showAuthMsg(msg, type = 'error') {
  const el = document.getElementById('authMsg')
  el.innerText   = msg
  el.className   = 'auth-msg ' + type
  el.style.display = 'block'
}

function clearAuthMsg() {
  const el = document.getElementById('authMsg')
  if (el) { el.style.display = 'none'; el.innerText = '' }
}

function goToProfile() {
  if (localStorage.getItem('user')) window.location.href = 'profile.html'
  else document.getElementById('authModal').style.display = 'flex'
}

function openProfile() {
  if (localStorage.getItem('user')) showProfile()
  else document.getElementById('authModal').style.display = 'flex'
}

async function login() {
  const username = document.getElementById('username').value.trim()
  const password = document.getElementById('password').value
  const email    = (document.getElementById('emailInput') || {}).value || ''

  if (!username || !password) { showAuthMsg('Please fill in all fields.'); return }

  const btn     = document.getElementById('authSubmitBtn')
  const btnText = document.getElementById('authBtnText')
  btn.disabled  = true
  const orig    = btnText.innerText
  btnText.innerText = 'Please wait…'
  clearAuthMsg()

  try {
    const body = { username, password }
    if (isSignup && email) body.email = email

    const res  = await fetch(`${API_URL}${isSignup ? '/register' : '/login'}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body)
    })
    const data = await res.json()

    if (res.ok) {
      showAuthMsg('Success! Redirecting…', 'success')
      localStorage.setItem('user', JSON.stringify({ id: data.id, name: data.username, email: data.email || email || null }))
      document.getElementById('username').value = ''
      document.getElementById('password').value = ''
      if (document.getElementById('emailInput')) document.getElementById('emailInput').value = ''
      setTimeout(() => {
        document.getElementById('authModal').style.display = 'none'
        window.location.href = 'profile.html'
      }, 800)
    } else {
      showAuthMsg(data.error || 'Authentication failed. Please try again.')
      btn.disabled  = false
      btnText.innerText = orig
    }
  } catch (e) {
    console.error(e)
    showAuthMsg('Connection error. Is the server running?')
    btn.disabled  = false
    btnText.innerText = orig
  }
}

function closeAuth() {
  document.getElementById('authModal').style.display = 'none'
  clearAuthMsg()
}



async function showProfile() {
  const userStr = localStorage.getItem('user')
  if (!userStr) return
  const user = JSON.parse(userStr)

  document.getElementById('profileName').innerText = '👤 ' + user.name
  document.getElementById('profileModal').style.display = 'flex'
  document.getElementById('profileHistoryList').innerHTML  = '<li>Loading…</li>'
  document.getElementById('profileFavoritesList').innerHTML = '<li>Loading…</li>'

  try {
    const res = await fetch(`${API_URL}/user/${user.id}`)
    if (!res.ok) return
    const data = await res.json()

    const hList = document.getElementById('profileHistoryList')
    hList.innerHTML = ''
    if (!data.history.length) {
      hList.innerHTML = '<li>No recent searches</li>'
    } else {
      data.history.forEach(h => {
        hList.innerHTML += `<li>${h.search_term}<small>${new Date(h.created_at).toLocaleDateString()}</small></li>`
      })
    }

    const fList = document.getElementById('profileFavoritesList')
    fList.innerHTML = ''
    if (!data.favorites.length) {
      fList.innerHTML = '<li>No favorite recipes yet</li>'
    } else {
      data.favorites.forEach(f => {
        fList.innerHTML += `
          <li style="cursor:pointer" onclick="openRecipe(${f.recipe_id})">
            ${f.recipe_name}
            <small>${new Date(f.created_at || Date.now()).toLocaleDateString()}</small>
            <button onclick="event.stopPropagation(); removeFavorite(${f.id})"
              style="display:inline-flex;align-items:center;background:#fef2f2;border:1px solid #fecaca;color:#b91c1c;border-radius:6px;padding:2px 8px;font-size:11px;margin-top:6px;cursor:pointer;font-family:inherit;font-weight:600;box-shadow:none;margin-left:0;">
              Remove ✕
            </button>
          </li>`
      })
    }
  } catch (e) { console.error(e) }
}

async function removeFavorite(favId) {
  const userStr = localStorage.getItem('user')
  if (!userStr) return
  const user = JSON.parse(userStr)
  if (confirm('Remove this favorite?')) {
    try {
      await fetch(`${API_URL}/favorites/${favId}?user_id=${user.id}`, { method: 'DELETE' })
      showProfile()
    } catch (e) { console.error(e) }
  }
}

function closeProfile() {
  document.getElementById('profileModal').style.display = 'none'
}

function logout() {
  localStorage.removeItem('user')
  document.getElementById('profileModal').style.display = 'none'
}



async function openRecipe(id) {
  const modal = document.getElementById('recipeModal')
  modal.style.display = 'flex'

  // Reset content
  document.getElementById('recipeTitle').innerText = 'Loading…'
  document.getElementById('recipeImage').src       = ''
  document.getElementById('recipeIngredients').innerHTML = ''
  document.getElementById('recipeInstructions').innerHTML = ''

  try {
    const res  = await fetch(`https://api.spoonacular.com/recipes/${id}/information?apiKey=f27dfecc2f80481bb246959ef390881b`)
    const data = await res.json()

    document.getElementById('recipeTitle').innerText = data.title
    document.getElementById('recipeImage').src       = data.image

    const ingList = document.getElementById('recipeIngredients')
    ingList.innerHTML = ''
    ;(data.extendedIngredients || []).forEach(i => {
      ingList.innerHTML += `<li>${i.original}</li>`
    })

    document.getElementById('recipeInstructions').innerHTML =
      data.instructions || '<em>No instructions available.</em>'
  } catch (e) {
    document.getElementById('recipeTitle').innerText = 'Failed to load recipe'
    console.error(e)
  }
}

function closeRecipe() {
  document.getElementById('recipeModal').style.display = 'none'
}



async function detectFromImage() {

  const btn = document.getElementById('detectBtn')

  if (!btn) return

  const file = uploadInput.files[0]

  if (!file) {
    alert('Upload a fridge image first!')
    return
  }

  btn.innerHTML = '<span>🔍 Detecting...</span>'
  btn.disabled = true

  try {

    const formData = new FormData()

    formData.append('image', file)

    const res = await fetch('http://127.0.0.1:5000/detect', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()

    if (!data.ingredients || data.ingredients.length === 0) {

      btn.innerHTML = '<span>🤔 No ingredients detected</span>'

      setTimeout(() => {
        btn.innerHTML = '<span>🔍 Detect Ingredients</span>'
        btn.disabled = false
      }, 2500)

      return
    }

    data.ingredients.forEach(item => {

      const label = item.toLowerCase().trim()

      if (!ingredients.includes(label)) {
        ingredients.push(label)
      }

    })

    displayIngredients()

    updateFindBtn()

    btn.innerHTML = `<span>✅ ${data.ingredients.length} ingredients detected!</span>`

    setTimeout(() => {
      btn.innerHTML = '<span>🔍 Detect Ingredients</span>'
      btn.disabled = false
    }, 2500)

  } catch (err) {

    console.error(err)

    btn.innerHTML = '<span>⚠️ Detection failed</span>'

    setTimeout(() => {
      btn.innerHTML = '<span>🔍 Detect Ingredients</span>'
      btn.disabled = false
    }, 2500)
  }
}