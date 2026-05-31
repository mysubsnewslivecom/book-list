# ---- Base image ----
ARG BUILD_IMAGE_NAME=docker.io/python
ARG BUILD_IMAGE_TAG=3.14.5-slim-trixie
FROM ${BUILD_IMAGE_NAME}:${BUILD_IMAGE_TAG}

# ---- Copy uv (fast Python package manager) ----
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ---- Metadata ----
ARG CI_COMMIT_SHA
ARG CI_COMMIT_REF_NAME
ARG CI_COMMIT_TAG
ARG CI_PROJECT_URL
ARG CI_PIPELINE_URL
ARG GITLAB_USER_EMAIL
ARG GITLAB_USER_LOGIN
ARG CI_PIPELINE_CREATED_AT

LABEL org.opencontainers.image.source=$CI_PROJECT_URL \
  org.opencontainers.image.created=$CI_PIPELINE_CREATED_AT \
  org.opencontainers.image.authors=$GITLAB_USER_EMAIL \
  org.opencontainers.image.url=$CI_PIPELINE_URL \
  org.opencontainers.image.documentation=$CI_PROJECT_URL/-/wikis/home \
  org.opencontainers.image.version=$CI_COMMIT_TAG \
  org.opencontainers.image.revision=$CI_COMMIT_SHA \
  org.opencontainers.image.vendor=$GITLAB_USER_LOGIN \
  org.opencontainers.image.licenses="MIT" \
  org.opencontainers.image.ref.name=$CI_COMMIT_REF_NAME \
  org.opencontainers.image.title="python-devcontainer" \
  org.opencontainers.image.description="Python devcontainer"

# ---- System dependencies ----
RUN apt-get update \
  && apt-get -y install --no-install-recommends \
  jq sudo build-essential vim curl locales lsb-release \
  openssh-client git bash bash-completion sqlite3 \
  ca-certificates direnv \
  && locale-gen en_US.UTF-8 \
  && update-ca-certificates \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && echo "en_US.UTF-8 UTF-8" | tee /etc/locale.gen \
  && locale-gen

ENV LANG=en_US.UTF-8

# ---- User setup ----
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
  && useradd --uid $USER_UID --gid $USER_GID -m -s /usr/bin/bash $USERNAME \
  && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
  && chmod 0440 /etc/sudoers.d/$USERNAME

# Optional Docker group (only useful if socket mounted)
RUN groupadd -f docker \
  && usermod -aG docker $USERNAME

# ---- Switch to user early (IMPORTANT) ----
USER $USERNAME
WORKDIR /home/$USERNAME

# ---- Starship prompt (user install, no curl|sh as root) ----
RUN mkdir -pv /home/$USERNAME/.config /home/$USERNAME/.local/bin \
  && touch /home/$USERNAME/.config/starship.toml \
  && curl -fsSL https://starship.rs/install.sh | sh -s -- -y

ENV PATH="/home/$USERNAME/.local/bin:$PATH"

# ---- Shell config ----
RUN echo 'eval "$(starship init bash)"' | tee -a ~/.bashrc \
  && echo 'eval "$(direnv hook bash)"' | tee -a ~/.bashrc \
  && echo 'alias daa="direnv allow ."' | tee -a ~/.bashrc \
  && starship preset pastel-powerline > ~/.config/starship.toml

# ---- Devcontainer-friendly env ----
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  UV_CACHE_DIR=/home/$USERNAME/.cache/uv \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1

# ---- Workspace ----
WORKDIR /workspaces

CMD [ "bash" ]
