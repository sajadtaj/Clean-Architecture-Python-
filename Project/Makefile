PROJECT_NAME=crypto_option_arbitrage
SRC_DIR=src/$(PROJECT_NAME)
CURRENT_USER:=$(shell whoami)
CURRENT_GROUP:=$(shell id -gn)

.PHONY: create clean set-permission help

create:
	@echo "📁 در حال بررسی مسیر پروژه $(PROJECT_NAME)..."
	@if [ ! -d "$(SRC_DIR)" ]; then \
		echo "🚀 ساخت ساختار پروژه $(PROJECT_NAME)"; \
		mkdir -p $(SRC_DIR)/core/entities; \
		mkdir -p $(SRC_DIR)/core/value_objects; \
		mkdir -p $(SRC_DIR)/use_cases; \
		mkdir -p $(SRC_DIR)/interfaces/api; \
		mkdir -p $(SRC_DIR)/interfaces/cli; \
		mkdir -p $(SRC_DIR)/interfaces/scheduler; \
		mkdir -p $(SRC_DIR)/infrastructure/data_providers; \
		mkdir -p $(SRC_DIR)/infrastructure/db; \
		mkdir -p $(SRC_DIR)/infrastructure/notifiers; \
		mkdir -p $(SRC_DIR)/config; \
		mkdir -p $(SRC_DIR)/tests; \
		touch $(SRC_DIR)/main.py; \
		touch $(SRC_DIR)/config/.env.example; \
		find $(SRC_DIR) -type d -exec touch {}/__init__.py \; ;\
		echo "✅ ساخت پروژه $(PROJECT_NAME) کامل شد."; \
	else \
		echo "⚠️ مسیر $(SRC_DIR) از قبل وجود دارد. هیچ تغییری اعمال نشد."; \
	fi

clean:
	@echo "⚠️ در حال حذف ساختار پروژه $(PROJECT_NAME)..."
	@rm -rf $(SRC_DIR)
	@echo "🗑️ ساختار حذف شد."

set-permission:
	@echo "🔐 در حال اعطای دسترسی به کاربر فعلی ($(CURRENT_USER)) روی پروژه..."
	@sudo chown -R $(CURRENT_USER):$(CURRENT_GROUP) src/
	@echo "✅ مالکیت پروژه به $(CURRENT_USER):$(CURRENT_GROUP) تغییر یافت."

help:
	@echo "📘 دستورات موجود:"
	@echo "  make create          # ساخت ساختار پروژه در مسیر src/"
	@echo "  make clean           # حذف ساختار پروژه"
	@echo "  make set-permission  # تغییر مالکیت پروژه به کاربر فعلی"
	@echo "  make help            # نمایش این راهنما"
