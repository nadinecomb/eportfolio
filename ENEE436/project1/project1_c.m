% Define the parameters for the two classes
mu1 = [3, 6];
cov1 = [1/2, 0; 0, 2];
mu2 = [3, -2];
cov2 = [2, 0; 0, 2];
prob = 0.5;

% Generate random samples from the multivariate normal distribution
data1 = mvnrnd(mu1, cov1, 1000);
data2 = mvnrnd(mu2, cov2, 1000);

% Create a scatter plot of the two classes
figure;
scatter(data1(:, 1), data1(:, 2), 'r.', 'DisplayName', 'Class 1');
hold on;
scatter(data2(:, 1), data2(:, 2), 'b.', 'DisplayName', 'Class 2');
hold on;


% Initialize variables for the optimization problem
n = 2000;
% put data into one nx2 matrix and set its labels in y
data = [data1; data2];
y = [ones(1000, 1); -1 * ones(1000, 1)];
f = -1 * ones(n, 1);  % Coefficients for the optimization
A = [y'; -y'; eye(n); -eye(n)];  % Constraint matrix (negative identity)
c = 1;  % A constant scalar for constraint vector
b = [0; 0; c * ones(n, 1); zeros(n, 1)];  % Constraint vector


% Calculate the G matrix (nxn)
G = zeros(n);
for i = 1:n
    for j = 1:n
        G(i,j) = y(i) * data(i, :) * data(j, :)' * y(j);
    end
end

[x,] = quadprog(G, f, A, b);

% find support vectors
svm = data(x > 1e-5, :);
svmy = y(x > 1e-5);
lambda = x(x > 1e-5);


% used to check that support vector was correct
% svmcheck = fitcsvm(data,y);

scatter(svm(:, 1), svm(:, 2), 'gO', 'DisplayName', 'Support Vector');
hold on;

% to solve for 2 we use the equation given during class
w = zeros(1, 2);
for i=1:height(svm)
    w = w + svm(i, :)*svmy(i)*lambda(i);
end
display(w)

% to solve for w0 we use the complimentary slackness equation
t = zeros(height(svm) , 1);
for i = 1:height(svm)
    t(i) = w * svm(i, :)';
end

% since w0 is a bias constant, we let w0 be the mean of yi - wTxi for all
% support vectors
w0 = mean(svmy - t);
display(w0)

% the decision boundary is w1x1 + w2x2 + w0 = 0 for each point
x1 = -4:14/2000:10;
x2 = (-w(1)*x1 - w0)/w(2);
plot(x1, x2, 'DisplayName', 'boundary');
hold off;
legend show;
xlabel('x1');
ylabel('x2');
title('Scatter Plot');
