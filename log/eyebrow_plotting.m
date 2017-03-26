A = csvread('eyebrows1.csv')
hold on
B = A(:,1)./A(:,2)
plot(A(:,1))
plot(A(:,2), 'Color', [1.0, 0.5, 0.0])
plot(A(:,3), 'Color', [0.5, 0.0, 1.0])
