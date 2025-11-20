# 📘 Mizan Balance Function  
### *A scale-invariant loss & similarity function for modern machine learning.*

---

## 🔍 What is Mizan?

The **Mizan Balance Function** measures **relative imbalance** between predictions and targets — unlike MSE, which only measures absolute error.

Where **MSE sees raw error**,  
**Mizan sees proportional error**.

---

## 🧠 Why Mizan?

Example: a 5-point error on small numbers is far worse than on large numbers.  
MSE treats both equally.  
Mizan understands scale:

```
L = |x - y|^p / (|x|^p + |y|^p + eps)
```

---

## 📦 Installation

Clone the repository:

```
git clone https://github.com/<your-username>/mizan-balance-function.git
```

---

## 🧩 PyTorch Usage

```python
from mizan_loss import MizanLoss, CombinedMSE_MizanLoss

criterion = CombinedMSE_MizanLoss(p=2.0, lambda_mizan=0.1)
total_loss, mse_loss, mizan_loss = criterion(y_pred, y_true)
```

---

## 🧪 Kaggle Notebook

Includes:

```
example_multiscale_regression.ipynb
```

---

## 📁 Repository Structure

```
mizan-balance-function/
│── mizan_loss.py
│── example_multiscale_regression.ipynb
│── README.md
│── LICENSE
│── CONTRIBUTING.md
│── setup.py
```

---

## 📝 License

This project is MIT licensed.